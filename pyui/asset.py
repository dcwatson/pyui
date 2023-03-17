import ctypes
import math

import sdl2
from sdl2.sdlimage import IMG_Load

from .geom import Rect


class SlicedAsset:
    """
    Support either 1-, 3-, or 9-slice image assets, laid out:

        0 1 2
        3 4 5
        6 7 8
    """

    def __init__(self, path, center=None, scale=2.0):
        self.surface = IMG_Load(path.encode("utf-8"))
        self.w = self.surface.contents.w
        self.h = self.surface.contents.h
        self.center = Rect(*center) if center else Rect(self.w, self.h)
        self.scale = scale
        self.texture_cache = {}
        self.slice_rects = self.get_slices()

    def __del__(self):
        if self.surface:
            sdl2.SDL_FreeSurface(self.surface)
        for texture in self.texture_cache.values():
            if texture:
                sdl2.SDL_DestroyTexture(texture)

    def get_slices(self):
        return [
            Rect((0, 0), (self.center.left, self.center.top)),
            Rect((self.center.left, 0), (self.center.width, self.center.top)),
            Rect((self.center.right, 0), (self.w - self.center.right, self.center.top)),
            Rect((0, self.center.top), (self.center.left, self.center.height)),
            self.center,
            Rect(
                (self.center.right, self.center.top),
                (self.w - self.center.right, self.center.height),
            ),
            Rect(
                (0, self.center.bottom), (self.center.left, self.h - self.center.bottom)
            ),
            Rect(
                (self.center.left, self.center.bottom),
                (self.center.width, self.h - self.center.bottom),
            ),
            Rect(
                (self.center.right, self.center.bottom),
                (self.w - self.center.right, self.h - self.center.bottom),
            ),
        ]

    def get_texture(self, renderer):
        key = id(renderer)
        if key not in self.texture_cache:
            self.texture_cache[key] = sdl2.SDL_CreateTextureFromSurface(
                renderer, self.surface
            )
        return self.texture_cache[key]

    def render(self, renderer, rect, alpha=255, scale=1.0):
        def _scale(v):
            return int(math.ceil(v / (self.scale / scale)))

        texture = self.get_texture(renderer)
        s = self.slice_rects
        mid_w = rect.width - _scale(s[0].width) - _scale(s[2].width)
        mid_h = rect.height - _scale(s[0].height) - _scale(s[6].height)
        x1 = rect.left + _scale(s[0].width)
        x2 = rect.right - _scale(s[2].width)
        y1 = rect.top + _scale(s[0].height)
        y2 = rect.bottom - _scale(s[6].height)
        rects = [
            Rect([rect.left, rect.top], [_scale(s[0].width), _scale(s[0].height)]),
            Rect([x1, rect.top], [mid_w, _scale(s[1].height)]),
            Rect([x2, rect.top], [_scale(s[2].width), _scale(s[2].height)]),
            Rect([rect.left, y1], [_scale(s[3].width), mid_h]),
            Rect([x1, y1], [mid_w, mid_h]),
            Rect([x2, y1], [_scale(s[5].width), mid_h]),
            Rect([rect.left, y2], [_scale(s[6].width), _scale(s[6].height)]),
            Rect([x1, y2], [mid_w, _scale(s[7].height)]),
            Rect([x2, y2], [_scale(s[8].width), _scale(s[8].height)]),
        ]
        sdl2.SDL_SetTextureAlphaMod(texture, alpha)
        for idx in range(len(s)):
            src = s[idx]
            dst = rects[idx]
            sdl2.SDL_RenderCopy(
                renderer, texture, ctypes.byref(src.sdl), ctypes.byref(dst.sdl)
            )
