from pyui.geom import Rect, Size
from pyui.state import Binding

from .base import View


class ProgressBar(View):
    def __init__(self, value: Binding, minimum=0, maximum=100, **options):
        super().__init__(**options)
        self.minimum = minimum
        self.maximum = maximum
        self.current = value

    def minimum_size(self):
        return Size(self.env.scaled(40), self.env.scaled(20))

    def content_size(self, available):
        return Size(available.w, self.env.scaled(20))

    def draw(self, renderer, rect):
        width = int((self.current.value - self.minimum) * rect.width / (self.maximum - self.minimum))
        track_rect = Rect(origin=(rect.left, rect.top), size=(rect.width, self.env.scaled(6)))
        bar_rect = Rect(origin=(rect.left, rect.top), size=(width, self.env.scaled(6)))
        self.env.draw(renderer, "progress.track", track_rect)
        if width > 0:
            self.env.draw(renderer, "progress.bar", bar_rect)
