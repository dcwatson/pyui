import enum
from collections import namedtuple

import sdl2

Point = namedtuple("Point", ("x", "y"), defaults=(0, 0))
Size = namedtuple("Size", ("w", "h"), defaults=(0, 0))


class Axis(enum.IntEnum):
    HORIZONTAL = 0
    VERTICAL = 1

    @property
    def cross(self):
        return Axis.HORIZONTAL if self.value == 1 else Axis.VERTICAL

    def size(self, main, cross):
        return Size(main, cross) if self.value == 0 else Size(cross, main)

    def point(self, main, cross):
        return Point(main, cross) if self.value == 0 else Point(cross, main)


class Priority(enum.IntEnum):
    OPTIONAL = 0
    LOW = 1
    NORMAL = 2
    HIGH = 3


class Alignment(enum.Enum):
    LEADING = 0.0
    CENTER = 0.5
    TRAILING = 1.0


class Rect:
    def __init__(self, origin=None, size=None):
        if isinstance(origin, int) and isinstance(size, int):
            # Shortcut for Rect(w, h) with origin (0, 0)
            self.origin = Point()
            self.size = Size(origin, size)
        else:
            self.origin = Point(*origin or (0, 0))
            self.size = Size(*size or (0, 0))

    top = property(lambda self: self.origin.y)
    left = property(lambda self: self.origin.x)
    bottom = property(lambda self: self.origin.y + self.size.h)
    right = property(lambda self: self.origin.x + self.size.w)

    width = property(lambda self: self.size.w)
    height = property(lambda self: self.size.h)

    @property
    def center(self):
        return Point(self.left + (self.width // 2), self.top + (self.height // 2))

    @property
    def sdl(self):
        # TODO: what are the memory implications of making this a property?
        return sdl2.SDL_Rect(self.origin.x, self.origin.y, self.size.w, self.size.h)

    def __repr__(self):
        return "Rect(origin={}, size={})".format(self.origin, self.size)

    def __add__(self, other):
        if isinstance(other, Insets):
            return Rect(
                origin=Point(self.origin.x - other.left, self.origin.y - other.top),
                size=Size(self.size.w + other.width, self.size.h + other.height),
            )
        raise ValueError()

    def __sub__(self, other):
        if isinstance(other, Insets):
            return Rect(
                origin=Point(self.origin.x + other.left, self.origin.y + other.top),
                size=Size(self.size.w - other.width, self.size.h - other.height),
            )
        raise ValueError()

    def __contains__(self, other):
        if isinstance(other, Point):
            return other.x >= self.left and other.y >= self.top and other.x <= self.right and other.y <= self.bottom
        raise ValueError()

    def scroll(self, pt):
        return Rect(origin=(self.left - pt.x, self.top - pt.y), size=self.size)


class Insets:
    def __init__(self, top=None, left=None, bottom=None, right=None):
        if isinstance(top, int) and left is None and bottom is None and right is None:
            self.top = top
            self.left = top
            self.bottom = top
            self.right = top
        else:
            self.top = int(top or 0)
            self.left = int(left or 0)
            self.bottom = int(bottom or 0)
            self.right = int(right or 0)

    def __repr__(self):
        return "Insets({}, {}, {}, {})".format(self.top, self.left, self.bottom, self.right)

    @property
    def width(self):
        return self.left + self.right

    @property
    def height(self):
        return self.top + self.bottom

    def scaled(self, by):
        return self.__class__(self.top * by, self.left * by, self.bottom * by, self.right * by)

    def __getitem__(self, axis):
        if isinstance(axis, Axis):
            if axis == Axis.HORIZONTAL:
                return self.width
            elif axis == Axis.VERTICAL:
                return self.height
        raise IndexError()

    def leading(self, axis):
        if axis == Axis.HORIZONTAL:
            return self.left
        elif axis == Axis.VERTICAL:
            return self.top
        raise ValueError()

    def trailing(self, axis):
        if axis == Axis.HORIZONTAL:
            return self.right
        elif axis == Axis.VERTICAL:
            return self.bottom
        raise ValueError()
