import sdl2
from sdl2.sdlgfx import boxRGBA, roundedBoxRGBA

from pyui.env import Environment
from pyui.geom import Alignment, Axis, Insets, Point, Priority, Rect, Size


class EnvironmentalView:
    def __init__(self):
        self.env = Environment(self.__class__.__name__)

    def font(self, font=None, size=None):
        if font:
            self.env.font = font
        if size:
            self.env.font_size = int(size)
        return self

    def shadow(self, *rgba):
        if not rgba or rgba[0] is None:
            self.env.text_shadow = None
        else:
            self.env.text_shadow = sdl2.SDL_Color(*rgba)
        return self

    def color(self, *rgba):
        if not rgba or rgba[0] is None:
            self.env.color = None
        elif isinstance(rgba[0], sdl2.SDL_Color):
            self.env.color = rgba[0]
        else:
            self.env.color = sdl2.SDL_Color(*rgba)
        return self

    def background(self, *rgba):
        if not rgba or rgba[0] is None:
            self.env.background = None
        else:
            self.env.background = sdl2.SDL_Color(*rgba)
        return self

    def radius(self, r):
        self.env.radius = self.env.scaled(int(r))
        return self

    def padding(self, *tlbr):
        self.env.padding = Insets(*tlbr).scaled(self.env.scale)
        return self

    def border(self, *tlbr):
        self.env.border = Insets(*tlbr).scaled(self.env.scale)
        return self

    def priority(self, p):
        self.env.priority = Priority[p.upper()] if isinstance(p, str) else Priority(p)
        return self

    def alignment(self, a):
        self.env.alignment = Alignment[a.upper()] if isinstance(a, str) else Alignment(a)
        return self

    def spacing(self, s):
        self.env.spacing = self.env.scaled(int(s))
        return self


class View(EnvironmentalView):
    interactive = False
    draws_focus = True
    dirty = False
    disabled = False
    scrollable = False

    # Hierarchy information.
    _window = None
    parent = None
    index = 0

    def __init__(self, *contents, **options):
        super().__init__()
        # Overall frame of the View, including padding and border.
        self.frame = Rect()
        # How this View is represented in navigation views such as TabView.
        self.item_view = None
        # Convenience for stashing stuff. Should probably clean this up.
        for name, value in options.items():
            setattr(self, name, value)
        # The raw (un-built) View instances under this one.
        self.contents = contents
        # Resolved and built list of subviews, after evaluating e.g. ForEach constructs.
        # This will be empty until rebuild is called, which happens on first layout and state changes.
        self.subviews = []

    @property
    def id(self):
        return "{}-{}".format(self.__class__.__name__, self.index)

    @property
    def id_path(self):
        path = []
        view = self
        while view:
            path.insert(0, view.id)
            view = view.parent
        return path

    @property
    def root(self):
        view = self
        while view.parent:
            view = view.parent
        return view

    @property
    def window(self):
        return self.root._window

    def __repr__(self):
        return self.id

    def __call__(self, *contents):
        self.contents = contents
        return self

    def __iter__(self):
        yield self

    def __getitem__(self, vid):
        if isinstance(vid, int):
            return self.subviews[vid]
        for view in self.subviews:
            if view.id == vid:
                return view

    def rebuild(self):
        new_subviews = []
        for idx, view in enumerate(self.content()):
            if not isinstance(view, View):
                raise ValueError("Subviews must be instances of View (got {}).".format(view.__class__.__name__))
            view.parent = self
            view.index = idx
            view.env.inherit(self.env)
            view.rebuild()
            new_subviews.append(view)
        # At some point, it may be worth diffing the subview tree and only replacing those that changed.
        self.subviews = new_subviews

    def content(self):
        for view in self.contents:
            yield from view

    def dump(self, level=0):
        indent = "  " * level
        print("{}{} {}".format(indent, self, self.frame))
        for view in self.subviews:
            view.dump(level + 1)

    def minimum_size(self):
        """
        Returns the minimum size in each dimension of this view's content, not including any padding or borders.
        """
        min_w = 0
        min_h = 0
        for view in self.subviews:
            m = view.minimum_size()
            min_w = max(m.w, min_w + view.env.padding[Axis.HORIZONTAL] + view.env.border[Axis.HORIZONTAL])
            min_h = max(m.h, min_h + view.env.padding[Axis.VERTICAL] + view.env.border[Axis.VERTICAL])
        return Size(min_w, min_h)

    def content_size(self, available: Size):
        """
        Given an available amount of space, returns the content size for this view's content, not including padding
        or borders.
        """
        return Size()

    def draw(self, renderer, rect):
        if self.env.background:
            rgba = (self.env.background.r, self.env.background.g, self.env.background.b, self.env.background.a)
            if self.env.radius:
                roundedBoxRGBA(
                    renderer,
                    self.frame.left,
                    self.frame.top,
                    self.frame.right,
                    self.frame.bottom,
                    self.env.radius,
                    *rgba
                )
            else:
                boxRGBA(renderer, self.frame.left, self.frame.top, self.frame.right, self.frame.bottom, *rgba)

    def resize(self, available: Size):
        """
        Sets the view's frame size, taking into account content size, padding, and borders.
        """
        max_w = 0
        max_h = 0
        inside = Size(
            max(0, available.w - self.env.padding.width - self.env.border.width),
            max(0, available.h - self.env.padding.height - self.env.border.height),
        )
        for view in self.subviews:
            view.resize(inside)
            max_w = max(max_w, view.frame.width)
            max_h = max(max_h, view.frame.height)
        size = self.content_size(inside)
        max_w = max(max_w, size.w)
        max_h = max(max_h, size.h)
        self.frame.size = Size(
            max_w + self.env.padding.width + self.env.border.width,
            max_h + self.env.padding.height + self.env.border.height,
        )

    def reposition(self, inside: Rect):
        """
        Sets the view's frame origin.
        """
        self.frame.origin = Point(
            inside.left + ((inside.width - self.frame.width) // 2),
            inside.top + ((inside.height - self.frame.height) // 2),
        )
        inner = inside - self.env.padding - self.env.border
        for view in self.subviews:
            view.reposition(inner)

    def layout(self, rect: Rect):
        if not self.subviews:
            self.rebuild()
        self.resize(rect.size)
        self.reposition(rect)
        self.dirty = False

    def render(self, renderer):
        inner = self.frame - self.env.padding - self.env.border
        self.draw(renderer, inner)
        for view in self.subviews:
            view.render(renderer)

    def disable(self, d):
        self.disabled = bool(d)
        return self

    def item(self, label_or_view):
        if isinstance(label_or_view, View):
            self.item_view = label_or_view
        elif callable(label_or_view):
            self.item_view = label_or_view()
        else:
            from .text import Text

            self.item_view = Text(label_or_view)
        return self

    def resolve(self, path):
        if not path or path[0] != self.id:
            return None
        view = self
        for part in path[1:]:
            view = view[part]
            if not view:
                return None
        return view

    def find(self, pt, **filters):
        if pt in self.frame:
            for view in self.subviews:
                found = view.find(pt, **filters)
                if found:
                    return found
            if all(getattr(self, attr, None) == value for attr, value in filters.items()):
                return self
        return None

    def find_all(self, **filters):
        found = []
        if all(getattr(self, attr, None) == value for attr, value in filters.items()):
            found.append(self)
        for view in self.subviews:
            found.extend(view.find_all(**filters))
        return found

    # Event handling stubs.

    def mousedown(self, pt):
        return True

    def mousemotion(self, pt):
        pass

    def mouseup(self, pt):
        pass

    def mousewheel(self, amt):
        pass

    def click(self, pt):
        pass

    def focus(self):
        pass

    def blur(self):
        pass

    def keydown(self, key, mods):
        pass

    def keyup(self, key, mods):
        pass

    def textinput(self, text):
        pass

    # State management.

    def state_changed(self, name, value):
        self.rebuild()
        self.root.dirty = True


class ForEach(View):
    def __init__(self, items, builder):
        super().__init__(items=items, builder=builder)

    def __iter__(self):
        for item in self.items:
            yield from self.builder(item)
