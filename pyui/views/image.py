import ctypes

import sdl2
from sdl2.sdlimage import IMG_Load, IMG_Load_RW

from pyui.geom import Size

from .base import View


class Image(View):
    def __init__(self, path=None, rw=None, clamped=True, stretch=False):
        assert path or rw
        super().__init__()
        self.path = path
        self.rw = rw
        self.clamped = clamped
        self.stretch = stretch
        # Cached locally, not copied on re-use.
        self._surface = None
        self._texture = None
        self._size = None

    def load_surface(self):
        if self._surface is None:
            if self.path:
                self._surface = IMG_Load(self.path.encode("utf-8"))
            else:
                self._surface = IMG_Load_RW(self.rw, 0)
            self._size = Size(self._surface.contents.w, self._surface.contents.h)

    @property
    def image_size(self):
        self.load_surface()
        return self._size

    def __del__(self):
        if self._surface:
            sdl2.SDL_FreeSurface(self._surface)
        if self._texture:
            sdl2.SDL_DestroyTexture(self._texture)

    def reuse(self, other):
        return self.path == other.path

    def constrain(self, available=None):
        if available is None:
            available = self.image_size
        box = self.env.constrain(available, self.image_size, clamped=self.clamped)
        if self.stretch:
            return box
        pct_w = box.w / self.image_size.w
        pct_h = box.h / self.image_size.h
        if pct_w < pct_h:
            return Size(box.w, int(self.image_size.h * pct_w))
        else:
            return Size(int(self.image_size.w * pct_h), box.h)

    def minimum_size(self):
        return self.constrain()

    def content_size(self, available: Size):
        return self.constrain(available)

    def draw(self, renderer, rect):
        self.load_surface()
        if self._texture is None:
            self._texture = sdl2.SDL_CreateTextureFromSurface(renderer, self._surface)
        sdl2.SDL_RenderCopy(renderer, self._texture, None, ctypes.byref(rect.sdl))
