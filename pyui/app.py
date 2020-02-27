import ctypes
import os

import rx
import rx.operators as ops
import rx.subject
import sdl2
from sdl2.sdlimage import IMG_INIT_PNG, IMG_Init
from sdl2.sdlttf import TTF_Init

from .env import Environment
from .font import Font
from .geom import Insets, Point, Rect, Size
from .theme import Theme


class Settings:
    def __init__(self, app_id):
        pass


class Window:
    def __init__(self, app, title, view, width=640, height=480, pack=False):
        self.app = app
        self.win = sdl2.SDL_CreateWindow(
            title.encode("utf-8"),
            sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED,
            width,
            height,
            sdl2.SDL_WINDOW_RESIZABLE | sdl2.SDL_WINDOW_ALLOW_HIGHDPI,
        )
        self.id = sdl2.SDL_GetWindowID(self.win)
        self.renderer = sdl2.SDL_CreateRenderer(self.win, -1, sdl2.SDL_RENDERER_ACCELERATED)
        self.view = view
        self.view._window = self
        self.background = self.view.env.theme.config["background"]
        # self.view.dump()
        # Which view is currently tracking mouse events (i.e. was clicked but not released yet)
        self.tracking = None
        # Which view has keyboard focus.
        self.focus = None
        self.focus_ring = self.view.env.theme.load_asset("focus")
        self.layout()
        if pack:
            scale = self.window_size.w / self.render_size.w
            self.resize(self.view.frame.width * scale, self.view.frame.height * scale)
            self.layout()
        # Listen for events
        self.listen(sdl2.SDL_MOUSEBUTTONDOWN, "button", self.mousedown)
        self.listen(sdl2.SDL_MOUSEBUTTONUP, "button", self.mouseup, check_window=False)
        self.listen(sdl2.SDL_MOUSEMOTION, "motion", self.mousemotion)
        self.listen(sdl2.SDL_MOUSEWHEEL, "wheel", self.mousewheel)
        self.listen(sdl2.SDL_WINDOWEVENT, "window", self.window_event)
        self.listen(sdl2.SDL_KEYDOWN, "key", self.key_event)
        self.listen(sdl2.SDL_KEYUP, "key", self.key_event)
        self.listen(sdl2.SDL_TEXTINPUT, "text", self.text_event)

    def listen(self, event_type, event_attr, handler, check_window=True):
        stream = self.app.events.pipe(ops.filter(lambda event: event.type == event_type), ops.pluck_attr(event_attr))
        if check_window:
            stream = stream.pipe(ops.filter(lambda event: event.windowID == self.id))
        # TODO: dispose of these when closing the window?
        stream.subscribe(handler)

    @property
    def window_size(self):
        w = ctypes.c_int()
        h = ctypes.c_int()
        sdl2.SDL_GetWindowSize(self.win, ctypes.byref(w), ctypes.byref(h))
        return Size(w.value, h.value)

    @property
    def render_size(self):
        w = ctypes.c_int()
        h = ctypes.c_int()
        sdl2.SDL_GetRendererOutputSize(self.renderer, ctypes.byref(w), ctypes.byref(h))
        return Size(w.value, h.value)

    def advance_focus(self, by=1):
        chain = self.view.find_all(interactive=True, disabled=False)
        current = self.view.resolve(self.focus)
        try:
            idx = (chain.index(current) + by) % len(chain)
        except ValueError:
            idx = by - 1 if by > 0 else by
        self.focus = chain[idx].id_path

    def resize(self, width, height):
        sdl2.SDL_SetWindowSize(self.win, int(width), int(height))

    def point(self, x, y):
        rs = self.render_size
        ws = self.window_size
        xs = rs.w / ws.w
        ys = rs.h / ws.h
        return Point(int(x * xs), int(y * ys))

    def layout(self):
        self.view.layout(Rect(size=self.render_size))

    def render(self):
        if self.view.dirty:
            self.layout()
        sdl2.SDL_SetRenderDrawColor(self.renderer, *self.background, sdl2.SDL_ALPHA_OPAQUE)
        sdl2.SDL_RenderClear(self.renderer)
        self.view.render(self.renderer)
        focus_view = self.view.resolve(self.focus)
        if focus_view and focus_view.draws_focus:
            focus_rect = focus_view.frame + Insets(focus_view.env.scaled(1))
            self.focus_ring.render(self.renderer, focus_rect)
        sdl2.SDL_RenderPresent(self.renderer)

    def cleanup(self):
        sdl2.SDL_DestroyRenderer(self.renderer)
        sdl2.SDL_DestroyWindow(self.win)

    # Event handlers

    def mousedown(self, event):
        pt = self.point(event.x, event.y)
        found = self.view.find(pt, interactive=True)
        if found and not found.disabled:
            found.mousedown(pt)
            self.tracking = found.id_path

    def mousemotion(self, event):
        pt = self.point(event.x, event.y)
        tracking_view = self.view.resolve(self.tracking)
        if tracking_view:
            tracking_view.mousemotion(pt)

    def mouseup(self, event):
        pt = self.point(event.x, event.y)
        found = self.view.find(pt, interactive=True)
        focus_view = self.view.resolve(self.focus)
        if focus_view and not found:
            self.focus = None
            focus_view.blur()
        tracking_view = self.view.resolve(self.tracking)
        if tracking_view:
            tracking_view.mouseup(pt)
            if tracking_view == found:
                self.focus = found.id_path
                found.focus()
                found.click(pt)
        self.tracking = None

    def mousewheel(self, event):
        x = ctypes.c_int()
        y = ctypes.c_int()
        sdl2.SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))
        pt = self.point(x.value, y.value)
        found = self.view.find(pt, scrollable=True)
        if found and not found.disabled:
            found.mousewheel(Point(event.x, event.y))

    def window_event(self, event):
        if event.event == sdl2.SDL_WINDOWEVENT_SIZE_CHANGED:
            self.layout()

    def key_event(self, event):
        focus_view = self.view.resolve(self.focus)
        if event.type == sdl2.SDL_KEYDOWN:
            if event.keysym.sym == sdl2.SDLK_TAB:
                self.advance_focus(-1 if (event.keysym.mod & sdl2.KMOD_SHIFT) != 0 else 1)
            elif event.keysym.sym == sdl2.SDLK_SPACE:
                if focus_view and not focus_view.disabled:
                    focus_view.click(focus_view.frame.center)
            if focus_view and not focus_view.disabled:
                focus_view.keydown(event.keysym.sym, event.keysym.mod)
        elif event.type == sdl2.SDL_KEYUP:
            if focus_view and not focus_view.disabled:
                focus_view.keyup(event.keysym.sym, event.keysym.mod)

    def text_event(self, event):
        focus_view = self.view.resolve(self.focus)
        if focus_view and not focus_view.disabled:
            focus_view.textinput(event.text.decode("utf-8"))


class Application:
    def __init__(self, app_id, settings=Settings):
        self.initialize()
        self.settings = settings(app_id)
        self.windows = []
        self.running = False
        self.events = rx.subject.Subject()
        self.events.pipe(ops.filter(lambda event: event.type == sdl2.SDL_QUIT)).subscribe(self.quit)

    def initialize(self):
        sdl2.SDL_Init(sdl2.SDL_INIT_EVERYTHING)
        IMG_Init(IMG_INIT_PNG)
        TTF_Init()
        # Initialize our font cache and calculate DPI scaling.
        Font.initialize()
        # Ugly hack to determine resolution scaling factor as early as possible.
        win = sdl2.SDL_CreateWindow(
            "ResolutionTest".encode("utf-8"),
            sdl2.SDL_WINDOWPOS_UNDEFINED,
            sdl2.SDL_WINDOWPOS_UNDEFINED,
            100,
            100,
            sdl2.SDL_WINDOW_HIDDEN | sdl2.SDL_WINDOW_ALLOW_HIGHDPI,
        )
        rend = sdl2.SDL_CreateRenderer(win, -1, sdl2.SDL_RENDERER_ACCELERATED)
        win_w = ctypes.c_int()
        win_h = ctypes.c_int()
        rend_w = ctypes.c_int()
        rend_h = ctypes.c_int()
        sdl2.SDL_GetWindowSize(win, ctypes.byref(win_w), ctypes.byref(win_h))
        sdl2.SDL_GetRendererOutputSize(rend, ctypes.byref(rend_w), ctypes.byref(rend_h))
        scale_w = rend_w.value / win_w.value
        scale_h = rend_h.value / win_h.value
        # Will this ever not be the case?
        assert scale_w == scale_h
        Environment.scale.default = scale_w
        sdl2.SDL_DestroyRenderer(rend)
        sdl2.SDL_DestroyWindow(win)
        if os.name == "nt" and False:
            Environment.theme.default = Theme("themes/uwp/config.json")

    def window(self, title, view):
        self.windows.append(Window(self, title, view))

    def run(self):
        self.running = True
        event = sdl2.SDL_Event()
        while self.running:
            if sdl2.SDL_WaitEvent(ctypes.byref(event)) != 0:
                self.events.on_next(event)
            self.render()
        self.cleanup()
        sdl2.SDL_Quit()

    def quit(self, event=None):
        self.running = False

    def render(self):
        for window in self.windows:
            window.render()

    def cleanup(self):
        for window in self.windows:
            window.cleanup()
        Font.cleanup()
