import json
import os

from pyui.geom import Size

from .base import View

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


class Text(View):
    def __init__(self, text, **options):
        super().__init__(**options)
        self.text = str(text)

    def reuse(self, other):
        return self.text == other.text

    @property
    def _font(self):
        return self.env.theme.font(self.env.font, self.env.font_size)

    def minimum_size(self):
        return self._font.measure(self.text)

    def content_size(self, available: Size):
        return self._font.measure(self.text, width=available.w)

    def draw(self, renderer, rect):
        super().draw(renderer, rect)
        self._font.draw(renderer, self.text, rect, self.env.color)


class Icon(Text):
    data = json.load(open(os.path.join(DATA_DIR, "icons.json")))

    def __init__(self, name, style=None, size=None):
        info = Icon.data["icons"][name]
        fontname = "{}/{}.otf".format(Icon.data["font"], style or info["sets"][0])
        super().__init__(info["text"])
        self.font(fontname, size)
