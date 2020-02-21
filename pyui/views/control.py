from pyui.geom import Insets, Rect, Size
from pyui.theme import Theme

from .base import View
from .stack import HStack
from .text import Text


class Button(HStack):
    interactive = True

    def __init__(self, label="", action=None, asset="button"):
        if not isinstance(label, View):
            label = Text(label)
        super().__init__(label)
        self.padding = Insets(9, 40, 11, 40)
        self.action = action
        self.pressed = False
        theme = Theme("themes/dark/config.json")
        self.asset = theme.load_asset(asset)
        self.down = theme.load_asset(asset + ".pressed")

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


class TextField(View):
    interactive = True

    def __init__(self, placeholder="Enter some text"):
        self.placeholder = Text(placeholder).foreground(200, 200, 200)
        super().__init__(self.placeholder)
        self.padding = Insets(9, 40, 11, 40)
        theme = Theme("themes/dark/config.json")
        self.asset = theme.load_asset("textfield")

    # def content_size(self, available):
    #    return Size(available.w, 28)

    def draw(self, renderer, rect):
        self.asset.render(renderer, self.frame)
        super().draw(renderer, rect)
