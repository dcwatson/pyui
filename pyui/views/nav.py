from sdl2.sdlgfx import boxRGBA, rectangleRGBA, roundedBoxRGBA, roundedRectangleRGBA

from pyui.geom import Size
from pyui.state import Binding, State

from .base import ForEach, View
from .control import SegmentedButton
from .stack import Alignment, HStack, Spacer, VStack
from .text import Text


class ListItem(HStack):
    interactive = True
    _action = None

    def action(self, method):
        self._action = method
        return self

    def click(self, pt):
        if self._action:
            self._action(self.index)


class List(VStack):
    interactive = True

    def __init__(self, items=None, builder=None, selection: Binding = None):
        self.selection = selection
        contents = []
        if items is not None:
            contents.append(ForEach(items, builder or self.default_builder))
        super().__init__(*contents, spacing=0, alignment=Alignment.LEADING)

    def default_builder(self, item):
        return Text(item)

    def click(self, pt):
        self.selection.value = []

    def item_click(self, index):
        if self.selection:
            if index in self.selection.value:
                self.selection.value = [idx for idx in self.selection.value if idx != index]
            else:
                self.selection.value = [index]

    def wrap(self, item, index):
        wrapped = ListItem(spacing=0)(item, Spacer()).action(self.item_click).pad(10)
        if self.selection and index in self.selection.value:
            wrapped.background(200, 200, 255, 16)
        return wrapped

    def content_size(self, available: Size):
        return available

    def content(self):
        for idx, item in enumerate(super().content()):
            yield self.wrap(item, idx)
        yield Spacer()

    def draw(self, renderer, rect):
        boxRGBA(renderer, self.frame.left, self.frame.top, self.frame.right, self.frame.bottom, 30, 32, 33, 255)
        rectangleRGBA(
            renderer, self.frame.left, self.frame.top, self.frame.right + 1, self.frame.bottom + 1, 79, 81, 81, 200
        )


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
