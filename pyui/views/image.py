import ctypes

import sdl2
from sdl2.sdlimage import IMG_Load

from pyui.geom import Size

from .base import View


class Image(View):
    def __init__(self, path):
        super().__init__()
        self.surface = IMG_Load(path.encode("utf-8"))
        self.texture = None
        self._scale = 1.0

    def __del__(self):
        if self.surface:
            sdl2.SDL_FreeSurface(self.surface)
        if self.texture:
            sdl2.SDL_DestroyTexture(self.texture)

    def reuse(self, other):
        self._scale = other._scale
        return True

    def minimum_size(self):
        return Size(int(self.surface.contents.w * self._scale), int(self.surface.contents.h * self._scale))

    def content_size(self, available: Size):
        return Size(int(self.surface.contents.w * self._scale), int(self.surface.contents.h * self._scale))

    def draw(self, renderer, rect):
        if self.texture is None:
            self.texture = sdl2.SDL_CreateTextureFromSurface(renderer, self.surface)
        sdl2.SDL_RenderCopy(renderer, self.texture, None, ctypes.byref(rect.sdl))

    def scale(self, scale):
        self._scale = scale
        return self

    def height(self, h):
        return self.scale(self.env.scaled(h) / self.surface.contents.h)

    def width(self, w):
        return self.scale(self.env.scaled(w) / self.surface.contents.w)
