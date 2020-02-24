import enum

import sdl2
from sdl2.sdlgfx import boxRGBA

from pyui.env import Environment
from pyui.geom import Insets, Rect, Size


class Priority(enum.IntEnum):
    OPTIONAL = 0
    LOW = 1
    NORMAL = 2
    HIGH = 3


class Alignment(enum.Enum):
    LEADING = 0.0
    CENTER = 0.5
    TRAILING = 1.0


class ForEach:
    def __init__(self, items, builder):
        self.items = items
        self.builder = builder

    def __iter__(self):
        for item in self.items:
            yield self.builder(item)


class View:
    priority = Priority.NORMAL
    interactive = False
    dirty = False

    # Hierarchy information.
    parent = None
    index = 0

    env = Environment()

    def __init__(self, *contents, **options):
        # Overall frame of the View, including padding and border.
        self.frame = Rect()
        self.padding = Insets()
        self.border = Insets()
        self.background_color = None
        self.item_view = None
        self.contents = contents
        self.subviews = []
        self.rebuild()

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

    def __repr__(self):
        return self.id

    def __call__(self, *contents):
        self.contents = contents
        self.rebuild()
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
                raise ValueError("Subviews must be instances of View.")
            view.parent = self
            view.index = idx
            view.env.inherit(self.env)
            new_subviews.append(view)
        # At some point, it may be worth diffing the subview tree and only replacing those that changed.
        self.subviews = new_subviews

    def content(self):
        for item in self.contents:
            yield from item

    def dump(self, level=0):
        indent = "  " * level
        print("{}{}".format(indent, self))
        for view in self.subviews:
            view.dump(level + 1)

    def minimum_size(self):
        """
        Returns the minimum size in each dimension of this view's content, not including any padding or borders.
        """
        return Size()

    def content_size(self, available: Size):
        """
        Given an available amount of space, returns the content size for this view's content, not including padding
        or borders.
        """
        return Size()

    def draw(self, renderer, rect):
        if self.background_color:
            boxRGBA(
                renderer,
                self.frame.left,
                self.frame.top,
                self.frame.right,
                self.frame.bottom,
                self.background_color.r,
                self.background_color.g,
                self.background_color.b,
                self.background_color.a,
            )

    def resize(self, available: Size):
        """
        Sets the view's frame size, taking into account content size, padding, and borders.
        """
        max_w = 0
        max_h = 0
        inside = Size(
            max(0, available.w - self.padding.width - self.border.width),
            max(0, available.h - self.padding.height - self.border.height),
        )
        for view in self.subviews:
            view.resize(inside)
            max_w = max(max_w, view.frame.width)
            max_h = max(max_h, view.frame.height)
        size = self.content_size(inside)
        max_w = max(max_w, size.w)
        max_h = max(max_h, size.h)
        self.frame.size = Size(
            max_w + self.padding.width + self.border.width, max_h + self.padding.height + self.border.height
        )

    def reposition(self, inside: Rect):
        """
        Sets the view's frame origin.
        """
        self.frame.origin = inside.origin
        inner = inside - self.padding - self.border
        for view in self.subviews:
            view.reposition(inner)

    def layout(self, rect: Rect):
        self.resize(rect.size)
        self.reposition(rect)
        self.dirty = False

    def render(self, renderer):
        inner = self.frame - self.padding - self.border
        self.draw(renderer, inner)
        for view in self.subviews:
            view.render(renderer)

    def pad(self, *args):
        self.padding = Insets(*args).scale(self.env.scale)
        return self

    def background(self, r, g, b, a=255):
        self.background_color = sdl2.SDL_Color(r, g, b, a)
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

    def mousedown(self, pt):
        pass

    def mousemotion(self, pt):
        pass

    def mouseup(self, pt):
        pass

    def click(self, pt):
        pass

    def state_changed(self, name, value):
        self.rebuild()
        self.root.dirty = True
