import ctypes
import math
import os

import sdl2
from sdl2.sdlttf import TTF_CloseFont, TTF_OpenFont


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
            font = TTF_OpenFont(path.encode("utf-8"), math.ceil(size * cls.scale))
            cls.cache[key] = font
        return cls.cache[key]

    @classmethod
    def cleanup(cls):
        for key, font in cls.cache.items():
            TTF_CloseFont(font)
        cls.cache = {}
