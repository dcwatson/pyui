import ctypes

import sdl2

from pyui.geom import Rect, Size
from pyui.state import Binding
from pyui.utils import enumerate_last

from .base import View
from .stack import HStack
from .text import Text


class Button(HStack):
    interactive = True

    def __init__(self, label=None, action=None, asset="button", **options):
        contents = []
        if label is not None:
            if not isinstance(label, View):
                label = Text(label)
            contents = [label]
        super().__init__(*contents, **options)
        self.action = action
        self.pressed = False
        self.asset = self.env.theme.load_asset(asset)
        self.down = self.env.theme.load_asset(asset + ".pressed")

    def draw(self, renderer, rect):
        super().draw(renderer, rect)
        asset = self.down if self.pressed else self.asset
        asset.render(renderer, self.frame)

    def mousedown(self, pt):
        self.pressed = True

    def mousemotion(self, pt):
        self.pressed = pt in self.frame

    def mouseup(self, pt):
        self.pressed = False

    def click(self, pt):
        if self.action:
            self.action()


class Slider(View):
    interactive = True

    def __init__(self, value: Binding, minimum=0, maximum=100, **options):
        super().__init__(**options)
        self.minimum = minimum
        self.maximum = maximum
        self.current = value
        self.slider = self.env.theme.load_asset("slider.track")
        self.knob = self.env.theme.load_asset("slider.knob")

    @property
    def span(self):
        return self.maximum - self.minimum

    def minimum_size(self):
        return Size(self.env.scaled(40), self.env.scaled(20))

    def content_size(self, available):
        return Size(available.w, self.env.scaled(20))

    def draw(self, renderer, rect):
        offset = int(self.current.value * rect.width / self.span) - self.env.scaled(10)
        slider_rect = Rect(origin=(rect.left, rect.top + self.env.scaled(7)), size=(rect.width, self.env.scaled(6)))
        knob_rect = Rect(origin=(rect.left + offset, rect.top), size=(self.env.scaled(20), self.env.scaled(20)))
        self.slider.render(renderer, slider_rect)
        self.knob.render(renderer, knob_rect)

    def _set(self, value):
        self.current.value = min(max(int(value), self.minimum), self.maximum)

    def mousemotion(self, pt):
        inner = self.frame - self.env.padding - self.env.border
        if pt.x >= inner.left and pt.x <= inner.right:
            pct = (pt.x - inner.left) / inner.width
            self._set(self.minimum + (pct * self.span))

    def click(self, pt):
        self.mousemotion(pt)

    def keydown(self, key, mods):
        amt = self.span // 10 if mods & sdl2.KMOD_SHIFT else 1
        if key == sdl2.SDLK_LEFT:
            self._set(self.current.value - amt)
        elif key == sdl2.SDLK_RIGHT:
            self._set(self.current.value + amt)


class TextField(View):
    interactive = True

    def __init__(self, text: Binding, placeholder="Enter some text", **options):
        self.text = text
        self.placeholder = Text(placeholder, shadow=False).color(150, 150, 150)
        super().__init__(**options)
        self.asset = self.env.theme.load_asset("textfield")

    def minimum_size(self):
        return Text(self.text.value).minimum_size()

    def content_size(self, available):
        return Size(available.w, 0)

    def content(self):
        yield Text(self.text.value) if self.text.value else self.placeholder

    def draw(self, renderer, rect):
        super().draw(renderer, rect)
        self.asset.render(renderer, self.frame)

    def focus(self):
        sdl2.SDL_StartTextInput()
        sdl2.SDL_SetTextInputRect(ctypes.byref(self.frame.sdl))

    def blur(self):
        sdl2.SDL_StopTextInput()

    def keydown(self, key, mods):
        if key == sdl2.SDLK_BACKSPACE:
            self.text.value = self.text.value[:-1]

    def textinput(self, text):
        self.text.value = self.text.value + text


class SegmentedButton(HStack):
    def __init__(self, selection: Binding, *contents, **options):
        self.selection = selection
        super().__init__(*contents, spacing=0, **options)

    def _index_asset(self, idx, is_last):
        if idx == 0:
            return "button" if is_last else "segment.left"
        else:
            return "segment.right" if is_last else "segment.center"

    def select(self, idx):
        self.selection.value = idx

    def content(self):
        for idx, item, is_last in enumerate_last(super().content()):
            asset = self._index_asset(idx, is_last)
            if idx == self.selection.value:
                asset += ".selected"
            yield Button(item, action=lambda idx=idx: self.select(idx), asset=asset)
