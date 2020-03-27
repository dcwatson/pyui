from pyui.geom import Alignment
from pyui.state import Binding

from .base import View
from .control import Button
from .stack import HStack, Spacer, VStack


class MenuItem(HStack):
    interactive = True

    async def mouseenter(self):
        self.background(0, 100, 200, 255)

    async def mouseleave(self):
        self.background(None)

    async def click(self, pt):
        pass


class Menu(VStack):
    def __init__(self, *contents, **options):
        super().__init__(*contents, alignment=Alignment.LEADING, **options)

    def draw(self, renderer, rect):
        super().draw(renderer, rect)
        self.env.draw(renderer, "menu", self.frame)


class Picker(View):
    interactive = True

    def __init__(self, selection: Binding, action=None, **options):
        self.selection = selection
        self.action = action
        super().__init__(**options)

    async def click(self, pt):
        items = [MenuItem(item, Spacer()) for item in super().content()]
        self.window.show_menu(Menu(*items).size(width=150), pt)

    def content(self):
        view = Button("Select", interactive=False)
        for idx, item in enumerate(super().content()):
            if idx == self.selection.value:
                pass  # view = Button(item, interactive=False)
        yield view
