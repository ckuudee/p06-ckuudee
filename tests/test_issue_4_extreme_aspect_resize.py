# Tests for issue #4: extreme aspect-ratio resizes.
# Each test is expected to FAIL on the current code, for the reason in the issue.

from io import BytesIO
from os.path import abspath, dirname, join

from PIL import Image
from tornado.testing import gen_test

from tests.handlers.test_base_handler import BaseImagingTestCase
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.importer import Importer

# course/images holds rainbow.png, 940x2.png, etc. named in issue #4.
COURSE_IMAGES_ROOT = abspath(
    join(dirname(__file__), "..", "course", "images")
)


class ExtremeAspectResizeTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = COURSE_IMAGES_ROOT
        cfg.STORAGE = "thumbor.storages.no_storage"
        cfg.QUALITY = "keep"
        cfg.SVG_DPI = 200

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        return Context(server, cfg, importer)

    @gen_test
    async def test_wide_resize_of_transparent_png_is_not_empty(self):
        # Issue #4: /unsafe/800x20/rainbow.png comes back fully transparent.
        response = await self.async_fetch("/unsafe/800x20/rainbow.png")
        assert response.code == 200
        image = Image.open(BytesIO(response.body))
        assert image.size == (800, 20)
        alpha = image.convert("RGBA").getchannel("A")
        assert alpha.getextrema() != (0, 0), (
            "resized transparent PNG is fully transparent"
        )

    @gen_test
    async def test_fit_in_1x1_returns_image_not_500(self):
        # Issue #4: /unsafe/fit-in/1x1/940x2.png returns a 500 error page.
        response = await self.async_fetch("/unsafe/fit-in/1x1/940x2.png")
        assert response.code == 200, f"got {response.code}, expected 200"
        image = Image.open(BytesIO(response.body))
        assert image.size == (1, 1)

    @gen_test
    async def test_fit_in_width_only_returns_image_not_500(self):
        # Issue #4: /unsafe/fit-in/100x0/940x2.png returns a 500 error page.
        response = await self.async_fetch("/unsafe/fit-in/100x0/940x2.png")
        assert response.code == 200, f"got {response.code}, expected 200"
        image = Image.open(BytesIO(response.body))
        assert image.size == (100, 1)
