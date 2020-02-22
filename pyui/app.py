import ctypes

import rx
import rx.operators as ops
import rx.subject
import sdl2
from sdl2.sdlimage import IMG_INIT_PNG, IMG_Init
from sdl2.sdlttf import TTF_Init

from .geom import Point, Rect, Size


class Settings:
    def __init__(self, app_id):
        pass


class Window:
    def __init__(self, app, title, view, width=640, height=480, pack=True):
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
        # self.view.dump()
        # Which view is currently tracking mouse events (i.e. was clicked but not released yet)
        self.tracking = None
        self.layout()
        if pack:
            scale = self.window_size.w / self.render_size.w
            self.resize(self.view.frame.width * scale, self.view.frame.height * scale)
            self.layout()
        # Listen for events
        self.listen(sdl2.SDL_MOUSEBUTTONDOWN, "button", self.mousedown)
        self.listen(sdl2.SDL_MOUSEBUTTONUP, "button", self.mouseup, check_window=False)
        self.listen(sdl2.SDL_MOUSEMOTION, "motion", self.mousemotion)
        self.listen(sdl2.SDL_WINDOWEVENT, "window", self.window_event)

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
        sdl2.SDL_SetRenderDrawColor(self.renderer, 48, 50, 51, sdl2.SDL_ALPHA_OPAQUE)
        sdl2.SDL_RenderClear(self.renderer)
        self.view.render(self.renderer)
        sdl2.SDL_RenderPresent(self.renderer)

    def cleanup(self):
        sdl2.SDL_DestroyRenderer(self.renderer)
        sdl2.SDL_DestroyWindow(self.win)

    # Event handlers

    def mousedown(self, event):
        pt = self.point(event.x, event.y)
        found = self.view.find(pt, interactive=True)
        if found:
            found.mousedown(pt)
            self.tracking = found

    def mousemotion(self, event):
        pt = self.point(event.x, event.y)
        if self.tracking:
            self.tracking.mousemotion(pt)

    def mouseup(self, event):
        pt = self.point(event.x, event.y)
        found = self.view.find(pt, interactive=True)
        if self.tracking:
            self.tracking.mouseup(pt)
            if self.tracking == found:
                found.click(pt)
            self.tracking = None

    def window_event(self, event):
        if event.event == sdl2.SDL_WINDOWEVENT_SIZE_CHANGED:
            self.layout()


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
