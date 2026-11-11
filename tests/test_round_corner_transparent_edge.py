# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from tornado.testing import gen_test

from tests.base import FilterTestCase


class RoundCornerTransparentEdgeTestCase(FilterTestCase):
    @gen_test
    async def test_transparent_corner_edge_pixels_are_partly_transparent(
        self,
    ):
        radius = 50
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.round_corner",
            f"round_corner({radius},255,0,0,1)",
            mode="RGBA",
        )

        # The top-left corner box holds the arc. Edge pixels on the arc
        # must fade through alpha, so some of them must be partly
        # transparent (0 < alpha < 255). Today they stay at alpha 255.
        pixels = image.load()
        partial = [
            pixels[x, y][3]
            for x in range(radius)
            for y in range(radius)
            if 0 < pixels[x, y][3] < 255
        ]

        assert len(partial) > 0, (
            "no partly transparent pixels on the corner arc; "
            "edge pixels are fully opaque"
        )
