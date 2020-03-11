from pyui.geom import Size

from .base import View


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
