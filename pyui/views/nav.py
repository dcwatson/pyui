from sdl2.sdlgfx import boxRGBA, rectangleRGBA, roundedBoxRGBA, roundedRectangleRGBA

from pyui.geom import Size
from pyui.state import State

from .base import ForEach, View
from .control import SegmentedButton
from .stack import Alignment, HStack, Spacer, VStack
from .text import Text


class List(VStack):
    def __init__(self, items, builder=None):
        super().__init__(ForEach(items, builder or self.default_builder), spacing=0, alignment=Alignment.LEADING)

    def default_builder(self, item):
        return Text(item).pad(10)

    def content_size(self, available: Size):
        return Size(0, available.h)

    def content(self):
        yield from super().content()
        yield Spacer()

    def draw(self, renderer, rect):
        boxRGBA(renderer, self.frame.left, self.frame.top, self.frame.right, self.frame.bottom, 30, 32, 33, 255)
        rectangleRGBA(renderer, self.frame.left, self.frame.top, self.frame.right, self.frame.bottom, 79, 81, 81, 255)


class TabView(View):
    selected = State(int, default=0)

    def content_size(self, available):
        return available

    def draw(self, renderer, rect):
        mid = self.env.scaled(13)
        roundedBoxRGBA(renderer, rect.left, rect.top + mid, rect.right, rect.bottom, 4, 79, 81, 81, 64)
        roundedRectangleRGBA(renderer, rect.left, rect.top + mid, rect.right, rect.bottom, 4, 79, 81, 81, 255)

    def content(self):
        tabs = list(super().content())
        show = tabs[self.selected.value] if tabs else View()
        # fmt: off
        yield VStack(spacing=0)(
            HStack(spacing=0)(
                Spacer(),
                SegmentedButton(self.selected, *[t.item_view for t in tabs]),
                Spacer(),
            ),
            show
        )
        # fmt: on
