import json
import os

from pyui.geom import Size

from .base import View

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
)


class Text(View):
    def __init__(self, text, **options):
        super().__init__(**options)
        self.text = str(text)
        self._min_cache = None
        self._width_cache = None
        self._size_cache = None
        self._line_cache = None

    def reuse(self, other):
        return self.text == other.text and self._font == other._font

    @property
    def _font(self):
        return self.env.theme.font(self.env.font, self.env.font_size)

    def minimum_size(self):
        if self._min_cache is None:
            self._min_cache = self._font.measure(self.text)
        return self._min_cache

    def content_size(self, available: Size):
        if self._size_cache is None or self._width_cache != available.w:
            self._width_cache = available.w
            self._size_cache = self._font.measure(self.text, width=available.w)
            self._line_cache = None
        return self._size_cache

    def draw(self, renderer, rect):
        super().draw(renderer, rect)
        self._line_cache = self._font.draw(
            renderer, self.text, rect, self.env.blended_color, lines=self._line_cache
        )


class Icon(Text):
    data = json.load(open(os.path.join(DATA_DIR, "icons.json")))

    def __init__(self, name, style=None, size=None):
        info = Icon.data["icons"][name]
        fontname = "{}/{}.otf".format(Icon.data["font"], style or info["sets"][0])
        super().__init__(info["text"])
        self.font(fontname, size)
