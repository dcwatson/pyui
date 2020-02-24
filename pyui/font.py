import ctypes

import sdl2
from sdl2.sdlttf import TTF_CloseFont, TTF_OpenFont


class Font:
    cache = {}
    scale = 1.0

    @classmethod
    def initialize(cls):
        ddpi = ctypes.c_float()
        if sdl2.SDL_GetDisplayDPI(0, ctypes.byref(ddpi), None, None) == 0:
            cls.scale = ddpi.value / 72.0

    @classmethod
    def load(cls, path, size):
        key = "{}-{}".format(path, size)
        if key not in cls.cache:
            font = TTF_OpenFont(path.encode("utf-8"), int(size * cls.scale))
            cls.cache[key] = font
        return cls.cache[key]

    @classmethod
    def cleanup(cls):
        for key, font in cls.cache.items():
            TTF_CloseFont(font)
        cls.cache = {}
