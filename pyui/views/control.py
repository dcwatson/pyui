from pyui.geom import Insets, Rect, Size
from pyui.state import Binding, State

from .base import View
from .stack import HStack
from .text import Text


class Button(HStack):
    interactive = True

    def __init__(self, label="", action=None, asset="button"):
        if not isinstance(label, View):
            label = Text(label)
        super().__init__(label)
        self.padding = Insets(5, 20, 6, 20).scale(self.env.scale)
        self.action = action
        self.pressed = False
        self.asset = self.env.theme.load_asset(asset)
        self.down = self.env.theme.load_asset(asset + ".pressed")

    def draw(self, renderer, rect):
        asset = self.down if self.pressed else self.asset
        asset.render(renderer, self.frame)
        super().draw(renderer, rect)

    def mousedown(self, pt):
        self.pressed = True

    def mouseup(self, pt):
        self.pressed = False

    def click(self, pt):
        if self.action:
            self.action()


class Slider(View):
    interactive = True

    def __init__(self, value: Binding, minimum=0, maximum=100):
        super().__init__()
        self.minimum = minimum
        self.maximum = maximum
        self.current = value
        self.slider = self.env.theme.load_asset("slider.track")
        self.knob = self.env.theme.load_asset("slider.knob")

    @property
    def span(self):
        return self.maximum - self.minimum

    def content_size(self, available):
        return Size(available.w, self.env.scaled(20))

    def draw(self, renderer, rect):
        offset = int(self.current.value * rect.width / self.span) - self.env.scaled(20)
        slider_rect = Rect(origin=(rect.left, rect.top + self.env.scaled(7)), size=(rect.width, self.env.scaled(6)))
        knob_rect = Rect(origin=(rect.left + offset, rect.top), size=(self.env.scaled(20), self.env.scaled(20)))
        self.slider.render(renderer, slider_rect)
        self.knob.render(renderer, knob_rect)

    def mousemotion(self, pt):
        inner = self.frame - self.padding - self.border
        if pt.x >= inner.left and pt.x <= inner.right:
            pct = (pt.x - inner.left) / inner.width
            self.current.value = int(self.minimum + (pct * self.span))

    def click(self, pt):
        self.mousemotion(pt)


class TextField(View):
    interactive = True

    def __init__(self, placeholder="Enter some text"):
        self.placeholder = Text(placeholder).foreground(200, 200, 200)
        super().__init__(self.placeholder)
        self.padding = Insets(4, 20, 5, 20).scale(self.env.scale)
        self.asset = self.env.theme.load_asset("textfield")

    # def content_size(self, available):
    #    return Size(available.w, 28)

    def draw(self, renderer, rect):
        self.asset.render(renderer, self.frame)
        super().draw(renderer, rect)
