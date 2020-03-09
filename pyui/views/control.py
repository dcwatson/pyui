import asyncio
import ctypes
import functools

import sdl2

from pyui.geom import Rect, Size
from pyui.state import Binding
from pyui.utils import clamp, enumerate_last

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
        self.asset = asset

    def draw(self, renderer, rect):
        super().draw(renderer, rect)
        asset_name = self.asset + ".pressed" if self.pressed else self.asset
        self.env.draw(renderer, asset_name, self.frame)

    async def mousedown(self, pt):
        self.pressed = True
        return True

    async def mousemotion(self, pt):
        self.pressed = pt in self.frame

    async def mouseup(self, pt):
        self.pressed = False

    async def click(self, pt):
        if self.action:
            if asyncio.iscoroutinefunction(self.action):
                asyncio.create_task(self.action())
            else:
                self.action()


class Slider(View):
    interactive = True

    def __init__(self, value: Binding, minimum=0, maximum=100, **options):
        super().__init__(**options)
        self.minimum = minimum
        self.maximum = maximum
        self.current = value

    @property
    def span(self):
        return self.maximum - self.minimum + 1

    def minimum_size(self):
        return Size(self.env.scaled(40), self.env.scaled(20))

    def content_size(self, available):
        return Size(available.w, self.env.scaled(20))

    def draw(self, renderer, rect):
        offset = int((self.current.value - self.minimum) * (rect.width - self.env.scaled(20)) / (self.span - 1))
        slider_rect = Rect(origin=(rect.left, rect.top + self.env.scaled(7)), size=(rect.width, self.env.scaled(6)))
        knob_rect = Rect(origin=(rect.left + offset, rect.top), size=(self.env.scaled(20), self.env.scaled(20)))
        self.env.draw(renderer, "slider.track", slider_rect)
        self.env.draw(renderer, "slider.knob", knob_rect)

    def _set(self, value):
        self.current.value = min(max(int(value), self.minimum), self.maximum)

    async def mousemotion(self, pt):
        inner = self.frame - self.env.padding - self.env.border
        pos = pt.x - inner.left
        pct = clamp(pos / inner.width, 0.0, 1.0)
        self._set(self.minimum + (pct * self.span))

    async def click(self, pt):
        await self.mousemotion(pt)

    async def keydown(self, key, mods):
        amt = self.span // 10 if mods & sdl2.KMOD_SHIFT else 1
        if key == sdl2.SDLK_LEFT:
            self._set(self.current.value - amt)
        elif key == sdl2.SDLK_RIGHT:
            self._set(self.current.value + amt)


class TextField(View):
    interactive = True

    def __init__(self, text: Binding, placeholder=None, **options):
        self.text = text
        self.placeholder = placeholder
        super().__init__(**options)

    def minimum_size(self):
        return Text(self.text.value).minimum_size()

    def content_size(self, available):
        return Size(available.w, 0)

    def content(self):
        if self.text.value:
            yield Text(self.text.value)
        elif self.placeholder:
            yield Text(self.placeholder).color(150, 150, 150)

    def draw(self, renderer, rect):
        super().draw(renderer, rect)
        self.env.draw(renderer, "textfield", self.frame)

    async def focus(self):
        sdl2.SDL_StartTextInput()
        sdl2.SDL_SetTextInputRect(ctypes.byref(self.frame.sdl))

    async def blur(self):
        sdl2.SDL_StopTextInput()

    async def keydown(self, key, mods):
        if key == sdl2.SDLK_BACKSPACE:
            self.text.value = self.text.value[:-1]

    async def textinput(self, text):
        self.text.value = self.text.value + text


class SegmentedButton(HStack):
    def __init__(self, selection: Binding, action=None, **options):
        self.selection = selection
        self.action = action
        super().__init__(spacing=0, **options)

    def _index_asset(self, idx, is_last):
        if idx == 0:
            return "button" if is_last else "segment.left"
        else:
            return "segment.right" if is_last else "segment.center"

    def select(self, idx):
        if self.action:
            self.action(idx)
        self.selection.value = idx

    def content(self):
        for idx, item, is_last in enumerate_last(super().content()):
            asset = self._index_asset(idx, is_last)
            if idx == self.selection.value:
                asset += ".selected"
            action = functools.partial(self.select, idx)
            yield Button(item, action=action, asset=asset).disable(self.disabled)
