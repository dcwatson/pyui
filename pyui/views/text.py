import ctypes

import sdl2
from sdl2.sdlttf import TTF_FontHeight, TTF_RenderUTF8_Blended, TTF_RenderUTF8_Blended_Wrapped, TTF_SizeUTF8

from pyui.geom import Rect, Size

from .base import View


class Text(View):
    def __init__(self, text, **options):
        super().__init__(**options)
        self.utf8 = str(text).encode("utf-8") or b" "
        self.surface = None
        self.shadow = None
        self.texture = None
        self.shadowtex = None

    def reuse(self, other):
        return self.utf8 == other.utf8

    @property
    def sdl_font(self):
        return self.env.theme.font(self.env.font, self.env.font_size)

    def free(self):
        if self.surface:
            sdl2.SDL_FreeSurface(self.surface)
            self.surface = None
        if self.shadow:
            sdl2.SDL_FreeSurface(self.shadow)
            self.shadow = None
        if self.texture:
            sdl2.SDL_DestroyTexture(self.texture)
            self.texture = None
        if self.shadowtex:
            sdl2.SDL_DestroyTexture(self.shadowtex)
            self.shadowtex = None

    def __del__(self):
        self.free()

    def create_surface(self, width=None):
        if self.surface and width and self.surface.contents.w == width:
            return
        self.free()
        if width:
            self.surface = TTF_RenderUTF8_Blended_Wrapped(self.sdl_font, self.utf8, self.env.color, width)
            if self.env.text_shadow:
                self.shadow = TTF_RenderUTF8_Blended_Wrapped(self.sdl_font, self.utf8, self.env.text_shadow, width)
        else:
            self.surface = TTF_RenderUTF8_Blended(self.sdl_font, self.utf8, self.env.color)
            if self.env.text_shadow:
                self.shadow = TTF_RenderUTF8_Blended(self.sdl_font, self.utf8, self.env.text_shadow)

    def update_texture(self, renderer):
        if self.surface and not self.texture:
            self.texture = sdl2.SDL_CreateTextureFromSurface(renderer, self.surface)
            if self.shadow:
                self.shadowtex = sdl2.SDL_CreateTextureFromSurface(renderer, self.shadow)

    def minimum_size(self):
        w = ctypes.c_int()
        h = ctypes.c_int()
        if TTF_SizeUTF8(self.sdl_font, self.utf8, ctypes.byref(w), ctypes.byref(h)) == 0:
            return Size(w.value, h.value)
        else:
            return Size(0, TTF_FontHeight(self.sdl_font))

    def content_size(self, available: Size):
        self.create_surface()
        return Size(self.surface.contents.w, self.surface.contents.h)

    def draw(self, renderer, rect):
        self.update_texture(renderer)
        super().draw(renderer, rect)
        if self.shadowtex:
            sr = Rect(origin=(rect.left + 1, rect.top + 1), size=(rect.width, rect.height))
            sdl2.SDL_RenderCopy(renderer, self.shadowtex, None, ctypes.byref(sr.sdl))
        sdl2.SDL_RenderCopy(renderer, self.texture, None, ctypes.byref(rect.sdl))
