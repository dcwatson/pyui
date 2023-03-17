from sdl2.sdlgfx import roundedBoxRGBA, roundedRectangleRGBA

from pyui.geom import Alignment, Size
from pyui.state import Binding, State

from .base import ForEach, View
from .control import SegmentedButton
from .stack import HStack, Spacer, VStack
from .text import Text


def ListHeaderStyle(view):
    return view.padding(10, 10, 5, 10).color(120, 120, 120).font(size=13)


class ListItem(HStack):
    interactive = True
    draws_focus = False
    _action = None

    def action(self, method):
        self._action = method
        return self

    async def click(self, pt):
        if self._action:
            self._action(self.index)


class ListContent(View):
    def __iter__(self):
        yield from self.contents


class List(VStack):
    interactive = True
    draws_focus = False

    def __init__(self, items=None, builder=None, selection: Binding = None, **options):
        self.selection = selection
        contents = []
        if items is not None:
            contents.append(ForEach(items, builder or self.default_builder))
        super().__init__(*contents, spacing=0, alignment=Alignment.LEADING, **options)

    def default_builder(self, item):
        return Text(item)

    async def click(self, pt):
        if self.selection is not None:
            self.selection.value = []

    def item_click(self, index):
        if self.selection is not None:
            self.window.focus = self.id_path
            if self.selection.value and index in self.selection.value:
                self.selection.value = [
                    idx for idx in self.selection.value if idx != index
                ]
            else:
                self.selection.value = [index]

    def wrap(self, item, index):
        wrapped = (
            ListItem(spacing=0)(item, Spacer()).action(self.item_click).padding(10)
        )
        if self.selection and self.selection.value and index in self.selection.value:
            wrapped.background(200, 200, 255, 16)
        return wrapped

    def content_size(self, available: Size):
        return available

    def content(self):
        for idx, item in enumerate(super().content()):
            yield item if isinstance(item, ListContent) else self.wrap(item, idx)
        yield HStack(Spacer())  # No! Bad!
        yield Spacer()


class Section(View):
    def __init__(self, header=None, footer=None, **options):
        super().__init__(**options)
        self.header = header
        self.footer = footer

    def __iter__(self):
        yield from self.content()

    def content(self):
        if self.header:
            if isinstance(self.header, View):
                yield ListContent(self.header)
            else:
                yield ListContent(Text(self.header).modify(ListHeaderStyle))
        yield from self.contents
        if self.footer:
            if isinstance(self.footer, View):
                yield ListContent(self.footer)
            else:
                yield ListContent(Text(self.footer).modify(ListHeaderStyle))


class TabView(View):
    selected = State(int, default=0)

    def content_size(self, available):
        return available

    def draw(self, renderer, rect):
        if self.env.background:
            rgb = (
                self.env.background.r,
                self.env.background.g,
                self.env.background.b,
            )
            mid = self.env.scaled(13)
            roundedBoxRGBA(
                renderer,
                rect.left,
                rect.top + mid,
                rect.right,
                rect.bottom,
                4,
                *rgb,
                64
            )
            roundedRectangleRGBA(
                renderer,
                rect.left,
                rect.top + mid,
                rect.right,
                rect.bottom,
                4,
                *rgb,
                255
            )

    def content(self):
        tabs = list(super().content())
        show = tabs[self.selected.value] if tabs else View()

        yield VStack(alignment=self.env.alignment, spacing=0)(
            SegmentedButton(self.selected)(*[t.item_view for t in tabs]), show, Spacer()
        )
