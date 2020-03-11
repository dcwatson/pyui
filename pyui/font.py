import ctypes
import math
import os

import sdl2
from sdl2.sdlttf import (
    TTF_HINTING_LIGHT,
    TTF_CloseFont,
    TTF_FontLineSkip,
    TTF_GetFontKerningSizeGlyphs,
    TTF_OpenFont,
    TTF_RenderGlyph_Blended,
    TTF_SetFontHinting,
)

from pyui.geom import Size


class Font:
    cache = {}
    scale = 1.0

    @classmethod
    def initialize(cls):
        ddpi = ctypes.c_float()
        base_dpi = 96.0 if os.name == "nt" else 72.0
        if sdl2.SDL_GetDisplayDPI(0, ctypes.byref(ddpi), None, None) == 0:
            cls.scale = ddpi.value / base_dpi

    @classmethod
    def load(cls, path, size):
        key = "{}-{}".format(path, size)
        if key not in cls.cache:
            cls.cache[key] = cls(path, size)
        return cls.cache[key]

    @classmethod
    def cleanup(cls):
        cls.cache = {}

    def __init__(self, path, size):
        self.path = path
        self.size = size
        self.font = TTF_OpenFont(path.encode("utf-8"), math.ceil(size * self.scale))
        TTF_SetFontHinting(self.font, TTF_HINTING_LIGHT)
        self.line_height = TTF_FontLineSkip(self.font)
        # A cache of surfaces that have been loaded for measuring, but not yet loaded into a texture.
        self.surfaces = {}
        # A cache of loaded textures and sizes per glyph.
        self.glyphs = {}

    def __del__(self):
        TTF_CloseFont(self.font)
        for surface, size in self.surfaces.values():
            sdl2.SDL_FreeSurface(surface)
        for tex, size in self.glyphs.values():
            sdl2.SDL_DestroyTexture(tex)

    def glyph_size(self, ch):
        assert isinstance(ch, int)
        if ch in self.glyphs:
            return self.glyphs[ch][1]
        elif ch not in self.surfaces:
            surface = TTF_RenderGlyph_Blended(self.font, ch, sdl2.SDL_Color(255, 255, 255))
            self.surfaces[ch] = (surface, Size(surface.contents.w, surface.contents.h))
        return self.surfaces[ch][1]

    def glyph(self, renderer, ch):
        assert isinstance(ch, int)
        if ch not in self.glyphs:
            # Pop the surface out of the cache and load it into a texture and the glyph cache.
            surface, size = self.surfaces.pop(ch, (None, None))
            if surface is None:
                surface = TTF_RenderGlyph_Blended(self.font, ch, sdl2.SDL_Color(255, 255, 255))
                size = Size(surface.contents.w, surface.contents.h)
            self.glyphs[ch] = (sdl2.SDL_CreateTextureFromSurface(renderer, surface), size)
            sdl2.SDL_FreeSurface(surface)
        return self.glyphs[ch]

    def prepare(self, renderer):
        # Pre-render the printable ASCII characters.
        for i in range(32, 127):
            self.glyph(renderer, i)

    def measure(self, text, width=None, kerning=True):
        lines = []
        w = 0
        prev = None
        for ch in text:
            code = ord(ch)
            if code == 10:
                lines.append(w)
                prev = None
                w = 0
                continue
            kern = TTF_GetFontKerningSizeGlyphs(self.font, prev, code) if kerning and prev else 0
            size = self.glyph_size(code)
            if width and (w + size.w + kern) > width:
                lines.append(w)
                prev = None
                w = size.w
            else:
                w += size.w + kern
                prev = code
        if w > 0:
            lines.append(w)
        if not lines:
            lines.append(0)
        max_w = max(lines) if lines else 0
        w = min(width, max_w) if width else max_w
        return Size(w, len(lines) * self.line_height)

    def draw(self, renderer, text, rect, color, kerning=True):
        x, y = rect.origin
        prev = None
        for ch in text:
            code = ord(ch)
            if code == 10:
                prev = None
                x = rect.left
                y += self.line_height
                continue
            kern = TTF_GetFontKerningSizeGlyphs(self.font, prev, code) if kerning and prev else 0
            tex, size = self.glyph(renderer, code)
            sdl2.SDL_SetTextureColorMod(tex, color.r, color.g, color.b)
            sdl2.SDL_SetTextureAlphaMod(tex, color.a)
            if x + size.w + kern > rect.right:
                prev = None
                kern = 0
                x = rect.left
                y += self.line_height
            dst = sdl2.SDL_Rect(x + kern, y, size.w, size.h)
            sdl2.SDL_RenderCopy(renderer, tex, None, ctypes.byref(dst))
            x += size.w + kern
            prev = code
