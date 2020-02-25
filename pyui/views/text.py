import ctypes

import sdl2
from sdl2.sdlttf import TTF_RenderUTF8_Blended, TTF_RenderUTF8_Blended_Wrapped

from pyui.geom import Rect, Size

from .base import View


class Text(View):
    def __init__(self, text):
        super().__init__()
        self.surface = None
        self.shadow = None
        self.texture = None
        self.shadowtex = None
        self.utf8 = str(text).encode("utf-8")
        self.font = self.env.theme.font()
        self.color = sdl2.SDL_Color(230, 230, 230)

    def __del__(self):
        if self.surface:
            sdl2.SDL_FreeSurface(self.surface)
        if self.shadow:
            sdl2.SDL_FreeSurface(self.shadow)
        if self.texture:
            sdl2.SDL_DestroyTexture(self.texture)
        if self.shadowtex:
            sdl2.SDL_DestroyTexture(self.shadowtex)

    def size(self, pts):
        self.font = self.env.theme.font(size=pts)
        return self

    def foreground(self, r, g, b):
        self.color = sdl2.SDL_Color(r, g, b)
        return self

    def create_surface(self, width=None):
        if self.surface and width and self.surface.contents.w == width:
            return
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
        shadow_color = sdl2.SDL_Color(0, 0, 0, 128)
        if width:
            self.surface = TTF_RenderUTF8_Blended_Wrapped(self.font, self.utf8, self.color, width)
            self.shadow = TTF_RenderUTF8_Blended_Wrapped(self.font, self.utf8, shadow_color, width)
        else:
            self.surface = TTF_RenderUTF8_Blended(self.font, self.utf8, self.color)
            self.shadow = TTF_RenderUTF8_Blended(self.font, self.utf8, shadow_color)

    def update_texture(self, renderer):
        if self.surface and not self.texture:
            self.texture = sdl2.SDL_CreateTextureFromSurface(renderer, self.surface)
            self.shadowtex = sdl2.SDL_CreateTextureFromSurface(renderer, self.shadow)

    def content_size(self, available: Size):
        self.create_surface(available.w)
        return Size(self.surface.contents.w, self.surface.contents.h)

    def draw(self, renderer, rect):
        self.update_texture(renderer)
        # sr = rect + Insets(right=1, bottom=1)
        sr = Rect(origin=(rect.left + 1, rect.top + 1), size=(rect.width, rect.height))
        sdl2.SDL_RenderCopy(renderer, self.shadowtex, None, ctypes.byref(sr.sdl))
        sdl2.SDL_RenderCopy(renderer, self.texture, None, ctypes.byref(rect.sdl))
