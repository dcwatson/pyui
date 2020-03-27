import asyncio
import ctypes
import os
import time

import rx
import rx.operators as ops
import rx.subject
import sdl2
from rx.scheduler.eventloop import AsyncIOScheduler
from sdl2.sdlimage import IMG_INIT_PNG, IMG_Init

from .env import Environment
from .font import Font
from .geom import Insets, Point, Rect, Size


class Settings:
    def __init__(self, app_id):
        pass


class Window:
    def __init__(self, app, title, view, width=640, height=480, resize=True, border=True, pack=False):
        self.app = app
        self.pack = pack
        self.needs_layout = True
        self.needs_render = True
        flags = sdl2.SDL_WINDOW_ALLOW_HIGHDPI
        if resize:
            flags |= sdl2.SDL_WINDOW_RESIZABLE
        if not border:
            flags |= sdl2.SDL_WINDOW_BORDERLESS
        self.win = sdl2.SDL_CreateWindow(
            title.encode("utf-8"),
            sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED,
            int(width * app.win_scale),
            int(height * app.win_scale),
            flags,
        )
        self.id = sdl2.SDL_GetWindowID(self.win)
        self.renderer = sdl2.SDL_CreateRenderer(self.win, -1, sdl2.SDL_RENDERER_ACCELERATED)
        self.view = view
        self.view._window = self
        self.view.env.theme.prepare(self.renderer)
        self.hover = None
        self.menu = None
        self.background = self.view.env.theme.config["background"]
        # self.view.dump()
        # Which view is currently tracking mouse events (i.e. was clicked but not released yet)
        self.tracking = None
        # Which view has keyboard focus.
        self.focus = None
        # List of running animations.
        self.animations = []
        # Debouncing state change observer.
        self.bouncer = rx.subject.Subject()
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
        # TODO: dispose of these subscriptions when closing the window?
        if asyncio.iscoroutinefunction(handler):

            async def handle_and_render(event):
                await handler(event)
                self.needs_render = True
                # self.render()

            stream.subscribe(lambda event: asyncio.create_task(handle_and_render(event)))
        else:
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

    def layout(self, force=False):
        if not self.needs_layout and not force:
            return
        self.needs_layout = False
        self.animations = []
        self.view.layout(Rect(size=self.render_size))

    def bounce_state_change(self, view):
        view.handle_state_change()

    def startup(self):
        self.bouncer.pipe(ops.sample(1.0 / 60.0)).subscribe(
            self.bounce_state_change, scheduler=AsyncIOScheduler(loop=asyncio.get_running_loop())
        )
        self.layout()
        if self.pack:
            scale = self.window_size.w / self.render_size.w
            self.resize(self.view.frame.width * scale, self.view.frame.height * scale)

    def animate(self, animation):
        self.animations.append(animation)
        # This is kind of a hack. The animations are triggered during layout, where the new frames are computed.
        # If we render that layout before starting the animation, it flashes at the new location, then back to the
        # original location and starts animating.
        self.needs_render = False

    def render(self, force=False):
        if not self.needs_render and not force:
            return
        # Set this up front, so that the act of rendering can request another render.
        self.needs_render = False
        sdl2.SDL_SetRenderDrawColor(self.renderer, *self.background, sdl2.SDL_ALPHA_OPAQUE)
        sdl2.SDL_RenderClear(self.renderer)
        self.view.render(self.renderer)
        focus_view = self.view.resolve(self.focus)
        if focus_view and focus_view.draws_focus:
            focus_rect = focus_view.frame + Insets(focus_view.env.scaled(1))
            self.view.env.draw(self.renderer, "focus", focus_rect)
        if self.menu:
            self.menu.render(self.renderer)
        sdl2.SDL_RenderPresent(self.renderer)

    def tick(self, dt):
        for a in self.animations:
            a.step(dt)
        self.animations = [a for a in self.animations if not a.finished()]
        self.layout()
        self.render()

    def cleanup(self):
        sdl2.SDL_DestroyRenderer(self.renderer)
        sdl2.SDL_DestroyWindow(self.win)

    def show_menu(self, menu, pt):
        self.menu = menu
        self.menu.rebuild()
        self.menu.resize(self.render_size)
        self.menu.reposition(Rect(origin=pt, size=self.menu.frame.size))

    def find(self, pt, **filters):
        for view in (self.menu, self.view):
            if view is None:
                continue
            found = view.find(pt, **filters)
            if found:
                return found
        return None

    def resolve(self, path):
        for view in (self.menu, self.view):
            if view is None:
                continue
            found = view.resolve(path)
            if found:
                return found
        return None

    # Event handlers

    async def mousedown(self, event):
        pt = self.point(event.x, event.y)
        found = self.find(pt, interactive=True)
        if found is None or found.disabled:
            found = self.view
        await found.mousedown(pt)
        self.tracking = found.id_path

    async def mousemotion(self, event):
        pt = self.point(event.x, event.y)
        current_hover = self.resolve(self.hover)
        if current_hover:
            await current_hover.hover(pt)
        found = self.find(pt)
        if found:
            self.hover = found.id_path
            if found != current_hover:
                await found.hover(pt)
        else:
            self.hover = None
        tracking_view = self.resolve(self.tracking)
        if tracking_view:
            await tracking_view.mousemotion(pt)

    async def mouseup(self, event):
        pt = self.point(event.x, event.y)
        found = self.find(pt, interactive=True)
        focus_view = self.resolve(self.focus)
        if focus_view and not found:
            self.focus = None
            await focus_view.blur()
        tracking_view = self.resolve(self.tracking)
        self.menu = None
        if tracking_view:
            await tracking_view.mouseup(pt)
            if tracking_view == found:
                self.focus = found.id_path
                await found.focus()
                await found.click(pt)
        self.tracking = None

    async def mousewheel(self, event):
        x = ctypes.c_int()
        y = ctypes.c_int()
        sdl2.SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))
        pt = self.point(x.value, y.value)
        found = self.find(pt, scrollable=True)
        if found is None or found.disabled:
            found = self.view
        await found.mousewheel(Point(-event.x, event.y))

    def window_event(self, event):
        # Note that this is not async because the loop is blocked during resizing.
        if event.event == sdl2.SDL_WINDOWEVENT_SIZE_CHANGED:
            self.layout(force=True)
            self.render(force=True)

    async def key_event(self, event):
        focus_view = self.resolve(self.focus)
        if focus_view is None or focus_view.disabled:
            focus_view = self.view
        if event.type == sdl2.SDL_KEYDOWN:
            if event.keysym.sym == sdl2.SDLK_TAB:
                self.advance_focus(-1 if (event.keysym.mod & sdl2.KMOD_SHIFT) != 0 else 1)
            elif event.keysym.sym == sdl2.SDLK_SPACE:
                if focus_view.interactive:
                    await focus_view.click(focus_view.frame.center)
            await focus_view.keydown(event.keysym.sym, event.keysym.mod)
        elif event.type == sdl2.SDL_KEYUP:
            await focus_view.keyup(event.keysym.sym, event.keysym.mod)

    async def text_event(self, event):
        focus_view = self.resolve(self.focus)
        if focus_view is None or focus_view.disabled:
            focus_view = self.view
        await focus_view.textinput(event.text.decode("utf-8"))


class Application:
    def __init__(self, app_id, settings=Settings):
        self.initialize()
        self.settings = settings(app_id)
        self.windows = []
        self.running = False
        self.events = rx.subject.Subject()
        self.events.pipe(ops.filter(lambda event: event.type == sdl2.SDL_QUIT)).subscribe(self.quit)

    def initialize(self):
        if os.name == "nt":
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        sdl2.SDL_Init(sdl2.SDL_INIT_EVERYTHING)
        IMG_Init(IMG_INIT_PNG)
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
        rend_w = ctypes.c_int()
        sdl2.SDL_GetWindowSize(win, ctypes.byref(win_w), None)
        sdl2.SDL_GetRendererOutputSize(rend, ctypes.byref(rend_w), None)
        # Windows HiDPI is silly like this. You get back different window sizes than you put in.
        self.win_scale = win_w.value / 100.0
        Environment.scale.default = rend_w.value / 100.0
        sdl2.SDL_DestroyRenderer(rend)
        sdl2.SDL_DestroyWindow(win)

    def window(self, title, view, **kwargs):
        win = Window(self, title, view, **kwargs)
        self.windows.append(win)
        return win

    def run(self):
        asyncio.run(self.run_async())

    async def run_async(self):
        self.running = True
        self.startup()

        def event_handler(data, event_ptr):
            if self.running:
                # SDL2 seems to re-use SDL_Event structures, so we need to make a copy.
                event = sdl2.SDL_Event()
                ctypes.pointer(event)[0] = event_ptr.contents
                self.events.on_next(event)
            return 0

        watcher = sdl2.SDL_EventFilter(event_handler)
        sdl2.SDL_AddEventWatch(watcher, None)

        fps = 60.0
        frame_time = 1.0 / fps
        last_tick = time.time()
        while self.running:
            sdl2.SDL_PumpEvents()
            # dt here will be how much time since the last loop minus any event handling.
            dt = time.time() - last_tick
            await asyncio.sleep(max(0, frame_time - dt))
            # dt here will be how much time since the last call to tick.
            dt = time.time() - last_tick
            self.tick(dt)
            last_tick = time.time()

        sdl2.SDL_DelEventWatch(watcher, None)
        self.cleanup()
        sdl2.SDL_Quit()

    def quit(self, event=None):
        self.running = False

    def startup(self):
        for window in self.windows:
            window.startup()

    def tick(self, dt):
        for window in self.windows:
            window.tick(dt)

    def cleanup(self):
        for window in self.windows:
            window.cleanup()
        Font.cleanup()
