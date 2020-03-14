import ctypes
import math
import os
import unicodedata

import sdl2
from sdl2.sdlttf import (
    TTF_HINTING_LIGHT,
    TTF_CloseFont,
    TTF_FontLineSkip,
    TTF_GetFontKerningSizeGlyphs,
    TTF_Init,
    TTF_OpenFont,
    TTF_RenderGlyph_Blended,
    TTF_SetFontHinting,
)

from .geom import Rect, Size
from .utils import enumerate_last


class Font:
    cache = {}
    scale = 1.0

    @classmethod
    def initialize(cls, scale=None):
        TTF_Init()
        if scale is None:
            ddpi = ctypes.c_float()
            base_dpi = 96.0 if os.name == "nt" else 72.0
            if sdl2.SDL_GetDisplayDPI(0, ctypes.byref(ddpi), None, None) == 0:
                cls.scale = ddpi.value / base_dpi
        else:
            cls.scale = scale

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
        if not self.font:
            raise Exception("Could not load font: {}".format(path))
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

    def words(self, text, kerning=True):
        """
        Yields a series of words (start/end index range) and the width of the word. Words are automatically broken by
        punctuation, spaces, or newlines. Unprintable characters are skipped (but break words).
        """
        start = 0
        width = 0
        prev = None
        textlen = len(text)
        for idx in range(textlen):
            code = ord(text[idx])
            if code == 10:
                # Newline.
                if idx > start:
                    yield start, idx, width
                yield idx, idx + 1, 0
                start = idx + 1
                width = 0
                prev = None
            elif code < 32:
                # Unprintable, ignore (but count as a word break).
                if idx > start:
                    yield start, idx, width
                start = idx + 1
                width = 0
                # Leave prev alone, so the next letter kerns over the unprintable character.
            else:
                size = self.glyph_size(code)
                kern = TTF_GetFontKerningSizeGlyphs(self.font, prev, code) if kerning and prev else 0
                if code == 32:
                    # Space, break word.
                    if idx > start:
                        yield start, idx, width
                    yield idx, idx + 1, size.w
                    start = idx + 1
                    width = 0
                elif unicodedata.category(text[idx]).startswith("P"):
                    # Punctuation, break word (including trailing punctuation).
                    width += size.w + kern
                    yield start, idx + 1, width
                    start = idx + 1
                    width = 0
                else:
                    # Printable character.
                    width += size.w + kern
                prev = code
        if textlen > start:
            yield start, textlen, width

    def layout(self, text, width, kerning=True):
        """
        Yields a series of lines, laying out text with a maximum width. Each line contains 0 or more tuples containing:
            (index_in_text, code_point, start_x, kerning, max_x)
        """
        x = 0
        prev = None
        line = []
        continuation = False
        for start, end, w in self.words(text):
            if x + w > width:
                prev = None
                x = 0
                continuation = True
                yield line
                line = []
            for idx in range(start, end):
                code = ord(text[idx])
                if code == 10:
                    prev = None
                    x = 0
                    continuation = False
                    yield line
                    line = []
                    continue
                if code == 32 and continuation:
                    continue
                kern = TTF_GetFontKerningSizeGlyphs(self.font, prev, code) if kerning and prev else 0
                size = self.glyph_size(code)
                if x + size.w + kern > width:
                    prev = None
                    kern = 0
                    x = 0
                    continuation = True
                    yield line
                    line = []
                line.append((idx, code, x, kern, x + size.w + kern))
                x += size.w + kern
                prev = code
                continuation = False
        yield line

    def measure(self, text, width=None, kerning=True):
        """
        Returns how much space the given text would take up when rendered, optionally with a width constraint.
        """
        max_x = 0
        y = 0
        for line in self.layout(text, width or 2 ** 14, kerning=kerning):
            if line:
                # Take the maximum extent of the last character on each line.
                max_x = max(max_x, line[-1][-1])
            y += self.line_height
        return Size(max_x, y)

    def find(self, text, rect, pt, kerning=True):
        """
        Given text laid out inside rect, finds the index in the text under the given point.
        """
        y = rect.top
        for line in self.layout(text, rect.width, kerning=kerning):
            for pos, (idx, code, x, kern, extent), last in enumerate_last(line):
                w = rect.width - x if last else extent - x
                r = Rect(origin=(rect.left + x, y), size=(w, self.line_height))
                if pt in r:
                    return idx
            y += self.line_height
        return None

    def draw(self, renderer, text, rect, color, selected=None, kerning=True):
        """
        Renders text in the specified rect, using the specified color. If specified, selected is a set of indexes in
        text that should be highlighted.
        """
        y = rect.top
        for line in self.layout(text, rect.width, kerning=kerning):
            for idx, code, x, kern, extent in line:
                tex, size = self.glyph(renderer, code)
                sdl2.SDL_SetTextureColorMod(tex, color.r, color.g, color.b)
                sdl2.SDL_SetTextureAlphaMod(tex, color.a)
                dst = sdl2.SDL_Rect(rect.left + x + kern, y, size.w, size.h)
                sdl2.SDL_RenderCopy(renderer, tex, None, ctypes.byref(dst))
                if selected and idx in selected:
                    sdl2.SDL_SetRenderDrawColor(renderer, 20, 60, 120, 255)
                    sdl2.SDL_SetRenderDrawBlendMode(renderer, sdl2.SDL_BLENDMODE_ADD)
                    sdl2.SDL_RenderFillRect(renderer, sdl2.SDL_Rect(rect.left + x, y, size.w + kern, size.h))
            y += self.line_height
