import ctypes

import sdl2

from pyui.geom import Axis, Insets, Point, Rect, Size
from pyui.utils import clamp

from .base import View


class ScrollView(View):
    interactive = True
    scrollable = True
    draws_focus = False

    def __init__(self, axis=Axis.VERTICAL, **options):
        super().__init__(**options)
        self.axis = Axis(axis) if axis is not None else None
        self.scroll_size = Size()
        self.scroll_interval = self.env.scaled(20)
        self.tracking = None
        self.offset = 0
        self.track_size = self.env.scaled(15)
        # Local state, not overwritten when re-using the view.
        self._position = Point()

    def content_size(self, available: Size):
        return available

    def knob_size(self):
        return Size(
            max(self.track_size, int(self.frame.width * self.frame.width / self.scroll_size[Axis.HORIZONTAL]))
            if self.scroll_size[Axis.HORIZONTAL] > self.frame.width
            else 0,
            max(self.track_size, int(self.frame.height * self.frame.height / self.scroll_size[Axis.VERTICAL]))
            if self.scroll_size[Axis.VERTICAL] > self.frame.height
            else 0,
        )

    def knob_position(self):
        size = self.knob_size()
        delta_w = max(0, self.scroll_size[Axis.HORIZONTAL] - self.frame.width)
        delta_h = max(0, self.scroll_size[Axis.VERTICAL] - self.frame.height)
        pct_w = self._position[Axis.HORIZONTAL] / delta_w if delta_w else 0
        pct_h = self._position[Axis.VERTICAL] / delta_h if delta_h else 0
        return Point(
            max(0, int((self.frame.width - size.w) * pct_w)), max(0, int((self.frame.height - size.h) * pct_h)),
        )

    def knob_rect(self, axis):
        size = self.knob_size()
        pos = self.knob_position()
        inner = self.frame - self.env.padding - self.env.border
        if axis == Axis.VERTICAL:
            return Rect(
                origin=(inner.right - self.env.scaled(13), inner.top + pos.y), size=(self.env.scaled(11), size.h)
            )
        else:
            return Rect(
                origin=(inner.left + pos.x, inner.bottom - self.env.scaled(13)), size=(size.w, self.env.scaled(11))
            )

    def resize(self, available: Size):
        available = self.env.constrain(available)
        # Need to account for scrollbars when resizing subviews.
        h = self.track_size if self.axis in (Axis.HORIZONTAL, None) else 0
        w = self.track_size if self.axis in (Axis.VERTICAL, None) else 0
        inside = Size(
            max(0, available.w - self.env.padding.width - self.env.border.width - w),
            max(0, available.h - self.env.padding.height - self.env.border.height - h),
        )
        self.scroll_size = super().resize(inside)
        self.frame.size = available
        # Clamp scroll positions when resizing.
        for axis in Axis:
            self.set_position(axis)
        return self.scroll_size

    def reposition(self, inside: Rect):
        # Account for scrollbars.
        bars = Insets()
        if self.axis in (Axis.VERTICAL, None):
            bars.right = self.track_size
        if self.axis in (Axis.HORIZONTAL, None):
            bars.bottom = self.track_size
        adjusted = inside - bars
        for view in self.subviews:
            scrolled = adjusted.scroll(self._position)
            # view.frame.origin = scrolled.origin
            view.reposition(scrolled)
            view.frame.origin = scrolled.origin
        self.frame.origin = inside.origin

    def set_position(self, axis, pos=None):
        delta = max(0, self.scroll_size[axis] - self.frame.size[axis])
        if pos is None:
            pos = self._position[axis]
        elif isinstance(pos, float):
            pos = int(delta * pos)
        self._position = axis.point(clamp(pos, 0, delta), self._position[axis.cross])

    async def mousedown(self, pt):
        for a in Axis:
            rect = self.knob_rect(a)
            if pt in rect:
                self.tracking = a
                self.offset = pt[a] - rect.origin[a]
                return True
        return False

    async def mousemotion(self, pt):
        if self.tracking is None:
            return
        size = self.knob_size()
        track = self.frame.size[self.tracking] - size[self.tracking]
        if not track:
            return
        pos = pt[self.tracking] - self.frame.origin[self.tracking] - self.offset
        self.set_position(self.tracking, pos / track)
        self.reposition(self.frame)

    async def mouseup(self, pt):
        self.tracking = None

    async def mousewheel(self, amt):
        axis = Axis.VERTICAL if amt.y != 0 else Axis.HORIZONTAL
        new_pos = self._position[axis] - (self.env.scaled(amt[axis]) * self.scroll_interval)
        self.set_position(axis, new_pos)
        self.reposition(self.frame)

    def render(self, renderer):
        # This is overridden so we can clip rendering to the visible bounds, and so we can draw our scrollbars last.
        inner = self.frame - self.env.padding - self.env.border
        sdl2.SDL_RenderSetClipRect(renderer, ctypes.byref(inner.sdl))
        for view in self.subviews:
            view.render(renderer)
        self.draw(renderer, inner)
        # sdl2.SDL_RenderSetClipRect(renderer, None)
        # Setting the clip rect to None/NULL work on OSX, but does strange things on Windows.
        # This is a hack, but seems to work.
        sdl2.SDL_RenderSetClipRect(renderer, ctypes.byref(self.root.frame.sdl))

    def draw(self, renderer, rect):
        super().draw(renderer, rect)

        if self.axis in (Axis.HORIZONTAL, None):
            w = rect.width - (0 if self.axis == Axis.HORIZONTAL else self.track_size)
            track_rect = Rect(origin=(rect.left, rect.bottom - self.track_size), size=(w, self.track_size))
            self.env.draw(renderer, "scroll.horizontal.track", track_rect)
            knob_rect = self.knob_rect(Axis.HORIZONTAL)
            if knob_rect.width:
                self.env.draw(renderer, "scroll.knob", knob_rect)

        if self.axis in (Axis.VERTICAL, None):
            h = rect.height - (0 if self.axis == Axis.VERTICAL else self.track_size)
            track_rect = Rect(origin=(rect.right - self.track_size, rect.top), size=(self.track_size, h))
            self.env.draw(renderer, "scroll.vertical.track", track_rect)
            knob_rect = self.knob_rect(Axis.VERTICAL)
            if knob_rect.height:
                self.env.draw(renderer, "scroll.knob", knob_rect)

        if self.axis is None:
            corner_rect = Rect(
                origin=(rect.right - self.track_size, rect.bottom - self.track_size),
                size=(self.track_size, self.track_size),
            )
            self.env.draw(renderer, "scroll.corner", corner_rect)
