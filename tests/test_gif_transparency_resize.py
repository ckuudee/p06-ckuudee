from io import BytesIO

from PIL import Image, ImageDraw

from thumbor.config import Config
from thumbor.context import Context
from thumbor.engines.pil import Engine


def make_context():
    cfg = Config(
        SECURITY_KEY="ACME-SEC",
        ENGINE="thumbor.engines.pil",
    )
    cfg.LOADER = "thumbor.loaders.file_loader"
    cfg.STORAGE = "thumbor.storages.no_storage"
    return Context(config=cfg)


def make_transparent_gif():
    # Palette GIF: index 0 is the background and is marked transparent,
    # index 1 is a blue disc, as in the sticker from issue #3.
    img = Image.new("P", (100, 100), 0)
    img.putpalette([255, 255, 255, 0, 0, 255] + [0, 0, 0] * 254)
    ImageDraw.Draw(img).ellipse((20, 20, 80, 80), fill=1)
    buffer = BytesIO()
    img.save(buffer, "GIF", transparency=0)
    return buffer.getvalue()


def test_resized_gif_keeps_transparent_background():
    engine = Engine(make_context())
    engine.load(make_transparent_gif(), ".gif")

    engine.resize(60, 60)
    output = Image.open(BytesIO(engine.read(".gif")))

    # The corner was transparent in the source. After the resize it must
    # still be transparent, not a solid opaque box.
    corner_alpha = output.convert("RGBA").getpixel((0, 0))[3]
    assert corner_alpha == 0, (
        "transparent background became opaque after resize"
    )
