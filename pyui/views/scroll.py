import ctypes

import sdl2

from pyui.geom import Axis, Insets, Point, Rect, Size
from pyui.utils import clamp

from .base import View


class ScrollView(View):
    interactive = True
    scrollable = True
    draws_focus = False

    axis = None

    def __init__(self, axis=None, **options):
        super().__init__(**options)
        self.scroll_size = Size()
        self.scroll_position = Point()
        self.scroll_interval = self.env.scaled(20)
        self.tracking = None
        self.offset = 0
        self.vtrack = self.env.theme.load_asset("scroll.vertical.track")
        self.knob = self.env.theme.load_asset("scroll.knob")

    def content_size(self, available: Size):
        return available

    def knob_size(self):
        return Size(
            min(self.frame.width, int(self.frame.width * self.frame.width / self.scroll_size[Axis.HORIZONTAL]))
            if self.scroll_size[Axis.HORIZONTAL] > self.frame.width
            else 0,
            min(self.frame.height, int(self.frame.height * self.frame.height / self.scroll_size[Axis.VERTICAL]))
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
                origin=(inner.right - self.env.scaled(13), inner.top + pos.y), size=(self.env.scaled(11), size.h),
            )
        else:
            return Rect(
                origin=(inner.left + pos.x, inner.bottom - self.env.scaled(13)), size=(size.w, self.env.scaled(11)),
            )

    def resize(self, available: Size):
        # Need to account for scrollbars when resizing subviews.
        inside = Size(
            max(0, available.w - self.env.padding.width - self.env.border.width - self.env.scaled(15)),
            max(0, available.h - self.env.padding.height - self.env.border.height),
        )
        super().resize(inside)
        self.frame.size = available

    def reposition(self, inside: Rect):
        max_w = 0
        max_h = 0
        # Account for scrollbars.
        adjusted = inside - Insets(right=self.env.scaled(15))
        for view in self.subviews:
            max_w = max(max_w, view.frame.width)
            max_h = max(max_h, view.frame.height)
            scrolled = adjusted.scroll(self.scroll_position)
            view.frame.origin = scrolled.origin
            view.reposition(scrolled)
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
        size = self.knob_size()
        if self.tracking == Axis.VERTICAL:
            track = self.frame.height - size.h
            if not track:
                return
            pos = pt.y - self.frame.top - self.offset
            pct = clamp(pos / track, 0.0, 1.0)
            delta_h = max(0, self.scroll_size[Axis.VERTICAL] - self.frame.height)
            self.scroll_position = Point(0, int(delta_h * pct))
            self.reposition(self.frame)

    def mousewheel(self, amt):
        new_pos = self.scroll_position.y - (self.env.scaled(amt.y) * self.scroll_interval)
        delta_h = max(0, self.scroll_size[Axis.VERTICAL] - self.frame.height)
        self.scroll_position = Point(0, clamp(new_pos, 0, delta_h))
        self.reposition(self.frame)

    def render(self, renderer):
        # This is overridden so we can clip rendering to the visible bounds, and so we can draw our scrollbars last.
        inner = self.frame - self.env.padding - self.env.border
        sdl2.SDL_RenderSetClipRect(renderer, ctypes.byref(inner.sdl))
        for view in self.subviews:
            view.render(renderer)
        self.draw(renderer, inner)
        sdl2.SDL_RenderSetClipRect(renderer, None)

    def draw(self, renderer, rect):
        super().draw(renderer, rect)

        vtrack_rect = Rect(origin=(rect.right - self.env.scaled(15), rect.top), size=(self.env.scaled(15), rect.height))
        self.vtrack.render(renderer, vtrack_rect)

        knob_rect = self.knob_rect(Axis.VERTICAL)
        if knob_rect.height:
            self.knob.render(renderer, knob_rect)
