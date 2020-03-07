import math

from sdl2.sdlgfx import thickLineRGBA

from pyui.geom import Size

from .base import View


class Spinner(View):
    def __init__(self, size=24, lines=12):
        super().__init__()
        self.d = self.env.scaled(size)
        self.lines = lines
        self.angles = [(math.pi * 2.0 / lines) * i for i in range(lines)]
        self.step = 0.0

    def minimum_size(self):
        return Size(self.env.scaled(10), self.env.scaled(10))

    def content_size(self, available: Size):
        return self.env.constrain(Size(self.d, self.d))

    def draw(self, renderer, rect):
        width = self.env.scaled(1)
        r1 = self.d / 4
        r2 = self.d / 2
        c = rect.center
        for idx, a in enumerate(self.angles):
            x1 = c.x + int(math.cos(a) * r1)
            y1 = c.y + int(math.sin(a) * r1)
            x2 = c.x + int(math.cos(a) * r2)
            y2 = c.y + int(math.sin(a) * r2)
            shade = 80 + (((idx - int(self.step)) % self.lines) * 6)
            thickLineRGBA(renderer, x1, y1, x2, y2, width, shade, shade, shade, 200)
        self.step += 0.25
        self.window.needs_render = True
