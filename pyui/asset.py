import ctypes

import sdl2

from .geom import Rect


class SlicedAsset:
    """
    Support either 1-, 3-, or 9-slice image assets, laid out:

        0 1 2
        3 4 5
        6 7 8
    """

    def __init__(self, surface, center=None):
        self.surface = surface
        self.w = self.surface.contents.w
        self.h = self.surface.contents.h
        self.center = Rect(*center) if center else Rect(self.w, self.h)
        self.texture = None

    def __del__(self):
        if self.texture:
            sdl2.SDL_DestroyTexture(self.texture)

    def slice_rects(self):
        yield Rect((0, 0), (self.center.left, self.center.top))
        yield Rect((self.center.left, 0), (self.center.width, self.center.top))
        yield Rect((self.center.right, 0), (self.w - self.center.right, self.center.top))
        yield Rect((0, self.center.top), (self.center.left, self.center.height))
        yield self.center
        yield Rect((self.center.right, self.center.top), (self.w - self.center.right, self.center.height))
        yield Rect((0, self.center.bottom), (self.center.left, self.h - self.center.bottom))
        yield Rect((self.center.left, self.center.bottom), (self.center.width, self.h - self.center.bottom))
        yield Rect((self.center.right, self.center.bottom), (self.w - self.center.right, self.h - self.center.bottom))

    def create_texture(self, renderer, rect):
        if not self.texture:
            self.texture = sdl2.SDL_CreateTextureFromSurface(renderer, self.surface)

    def render(self, renderer, rect, alpha=255):
        self.create_texture(renderer, rect)
        s = list(self.slice_rects())
        mid_w = rect.width - s[0].width - s[2].width
        mid_h = rect.height - s[0].height - s[6].height
        x1 = rect.left + s[0].width
        x2 = rect.right - s[2].width
        y1 = rect.top + s[0].height
        y2 = rect.bottom - s[6].height
        rects = [
            Rect([rect.left, rect.top], [s[0].width, s[0].height]),
            Rect([x1, rect.top], [mid_w, s[1].height]),
            Rect([x2, rect.top], [s[2].width, s[2].height]),
            Rect([rect.left, y1], [s[3].width, mid_h]),
            Rect([x1, y1], [mid_w, mid_h]),
            Rect([x2, y1], [s[5].width, mid_h]),
            Rect([rect.left, y2], [s[6].width, s[6].height]),
            Rect([x1, y2], [mid_w, s[7].height]),
            Rect([x2, y2], [s[8].width, s[8].height]),
        ]
        sdl2.SDL_SetTextureAlphaMod(self.texture, alpha)
        for idx in range(len(s)):
            src = s[idx]
            dst = rects[idx]
            sdl2.SDL_RenderCopy(renderer, self.texture, ctypes.byref(src.sdl), ctypes.byref(dst.sdl))
