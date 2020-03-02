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
        self.scroll_position = Point()
        self.scroll_interval = self.env.scaled(20)
        self.tracking = None
        self.offset = 0
        self.htrack = self.env.theme.load_asset("scroll.horizontal.track")
        self.vtrack = self.env.theme.load_asset("scroll.vertical.track")
        self.knob = self.env.theme.load_asset("scroll.knob")
        self.corner = self.env.theme.load_asset("scroll.corner")
        self.track_size = self.env.scaled(15)

    def content_size(self, available: Size):
        return available

    def knob_size(self):
        return Size(
            int(self.frame.width * self.frame.width / self.scroll_size[Axis.HORIZONTAL])
            if self.scroll_size[Axis.HORIZONTAL] > self.frame.width
            else 0,
            int(self.frame.height * self.frame.height / self.scroll_size[Axis.VERTICAL])
            if self.scroll_size[Axis.VERTICAL] > self.frame.height
            else 0,
        )

    def knob_position(self):
        size = self.knob_size()
        delta_w = max(0, self.scroll_size[Axis.HORIZONTAL] - self.frame.width)
        delta_h = max(0, self.scroll_size[Axis.VERTICAL] - self.frame.height)
        pct_w = self.scroll_position[Axis.HORIZONTAL] / delta_w if delta_w else 0
        pct_h = self.scroll_position[Axis.VERTICAL] / delta_h if delta_h else 0
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
        super().resize(inside)
        self.frame.size = available

    def reposition(self, inside: Rect):
        max_w = 0
        max_h = 0
        # Account for scrollbars.
        bars = Insets()
        if self.axis in (Axis.VERTICAL, None):
            bars.right = self.track_size
        if self.axis in (Axis.HORIZONTAL, None):
            bars.bottom = self.track_size
        adjusted = inside - bars
        for view in self.subviews:
            max_w = max(max_w, view.frame.width)
            max_h = max(max_h, view.frame.height)
            scrolled = adjusted.scroll(self.scroll_position)
            view.frame.origin = scrolled.origin
            view.reposition(scrolled)
            view.frame.origin = scrolled.origin
        self.frame.origin = inside.origin
        self.scroll_size = Size(max_w, max_h)

    def mousedown(self, pt):
        for a in Axis:
            rect = self.knob_rect(a)
            if pt in rect:
                self.tracking = a
                self.offset = pt[a] - rect.origin[a]
                return True
        return False

    def mousemotion(self, pt):
        if self.tracking is None:
            return
        size = self.knob_size()
        track = self.frame.size[self.tracking] - size[self.tracking]
        if not track:
            return
        pos = pt[self.tracking] - self.frame.origin[self.tracking] - self.offset
        pct = clamp(pos / track, 0.0, 1.0)
        delta = max(0, self.scroll_size[self.tracking] - self.frame.size[self.tracking])
        self.scroll_position = self.tracking.point(int(delta * pct), self.scroll_position[self.tracking.cross])
        self.reposition(self.frame)

    def mouseup(self, pt):
        self.tracking = None

    def mousewheel(self, amt):
        axis = Axis.VERTICAL if amt.y != 0 else Axis.HORIZONTAL
        new_pos = self.scroll_position[axis] - (self.env.scaled(amt[axis]) * self.scroll_interval)
        delta = max(0, self.scroll_size[axis] - self.frame.size[axis])
        self.scroll_position = axis.point(clamp(new_pos, 0, delta), self.scroll_position[axis.cross])
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
            self.htrack.render(renderer, track_rect)
            knob_rect = self.knob_rect(Axis.HORIZONTAL)
            if knob_rect.width:
                self.knob.render(renderer, knob_rect)

        if self.axis in (Axis.VERTICAL, None):
            h = rect.height - (0 if self.axis == Axis.VERTICAL else self.track_size)
            track_rect = Rect(origin=(rect.right - self.track_size, rect.top), size=(self.track_size, h))
            self.vtrack.render(renderer, track_rect)
            knob_rect = self.knob_rect(Axis.VERTICAL)
            if knob_rect.height:
                self.knob.render(renderer, knob_rect)

        if self.axis is None:
            corner_rect = Rect(
                origin=(rect.right - self.track_size, rect.bottom - self.track_size),
                size=(self.track_size, self.track_size),
            )
            self.corner.render(renderer, corner_rect)
