from sdl2.sdlgfx import boxRGBA, rectangleRGBA, roundedBoxRGBA, roundedRectangleRGBA

from pyui.geom import Size
from pyui.state import State

from .base import View
from .control import Button
from .stack import Alignment, HStack, Spacer, VStack
from .text import Text


class List(VStack):
    def __init__(self, items, builder=None):
        self.items = items
        self.builder = builder or self.default_builder
        super().__init__(spacing=0, alignment=Alignment.LEADING)

    def default_builder(self, item):
        return Text(item).pad(20)

    def content_size(self, available: Size):
        return Size(0, available.h)

    def content(self):
        for item in self.items:
            yield self.builder(item)
        yield Spacer()

    def draw(self, renderer, rect):
        boxRGBA(renderer, self.frame.left, self.frame.top, self.frame.right, self.frame.bottom, 30, 32, 33, 255)
        # rectangleRGBA(renderer, self.frame.left, self.frame.top, self.frame.right, self.frame.bottom, 79, 81, 81, 255)


class TabView(View):
    selected = State(int, default=0)

    def __init__(self):
        self.tabs = []
        super().__init__()

    def __call__(self, *tabs):
        self.tabs = tabs
        return self.rebuild()

    def content_size(self, available):
        return available

    def draw(self, renderer, rect):
        roundedBoxRGBA(renderer, rect.left, rect.top + 26, rect.right, rect.bottom, 4, 79, 81, 81, 64)
        roundedRectangleRGBA(renderer, rect.left, rect.top + 26, rect.right, rect.bottom, 4, 79, 81, 81, 255)

    def select(self, idx):
        self.selected = idx

    def content(self):
        assets = {}
        if len(self.tabs) == 1:
            assets[0] = "button"
        else:
            assets[0] = "segment.left"
            assets[len(self.tabs) - 1] = "segment.right"
        if self.selected in assets:
            assets[self.selected] += ".selected"
        else:
            assets[self.selected] = "segment.center.selected"
        buttons = [
            Button(t.item_view, action=lambda idx=idx: self.select(idx), asset=assets.get(idx, "segment.center"))
            for idx, t in enumerate(self.tabs)
        ]
        show = self.tabs[self.selected] if self.tabs else View()
        # fmt: off
        yield VStack(spacing=0)(
            HStack(spacing=0)(
                Spacer(),
                *buttons,
                Spacer(),
            ),
            show
        )
        # fmt: on
