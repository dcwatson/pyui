import os

import sdl2

from pyui.geom import Alignment, Axis, Insets, Priority, Size
from pyui.utils import clamp

from .theme import Theme

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Env:
    def __init__(self, inherit=False, default=None):
        self.name = None
        self.default = default
        self.inherit = inherit

    def __get__(self, instance, owner=None):
        if not instance:
            return self
        if self.name not in instance.__dict__:
            parent = instance.__dict__["parent"]
            if parent and self.inherit:
                return getattr(parent, self.name)
            return self.get_default()
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name

    def get_default(self):
        return self.default() if callable(self.default) else self.default


class Environment:
    theme = Env(inherit=True, default=Theme(os.path.join(BASE_DIR, "themes/dark/config.json")))
    scale = Env(inherit=True, default=1.0)

    font = Env(inherit=True, default="default")
    font_size = Env(inherit=True)
    text_shadow = Env(inherit=True)
    color = Env(default=sdl2.SDL_Color(0, 0, 0))
    background = Env()
    radius = Env(default=0)
    padding = Env(default=Insets(0))
    border = Env(default=Insets(0))
    priority = Env(default=Priority.NORMAL)
    alignment = Env(default=Alignment.CENTER)
    spacing = Env(default=0)
    size = Env(default=Size())
    opacity = Env(default=1.0, inherit=True)
    animation = Env(inherit=True)
    lines = Env(default=1)

    alpha = property(lambda self: round(self.opacity * 255))

    def __init__(self, class_name=None, **overrides):
        self.parent = None
        if class_name:
            self.load(class_name)
        for key, value in overrides.items():
            setattr(self, key, value)

    def inherit(self, parent):
        self.parent = parent

    def scaled(self, value):
        if value is None:
            return None
        return value.__class__(value * self.scale)

    def constrain(self, available, value=None, clamped=True):
        final = list(value or available)
        for a in Axis:
            v = self.size[a]
            if v:
                final[a] = v if isinstance(v, int) else int(v * available[a])
            if clamped:
                final[a] = clamp(final[a], 0, available[a])
        return Size(*final)

    def load(self, class_name):
        for key, value in self.theme.env(class_name.lower()).items():
            if key in ("padding", "border"):
                value = Insets(*value).scaled(self.scale)
            elif key in ("color", "background", "text_shadow"):
                value = sdl2.SDL_Color(*value)
            elif key == "priority":
                value = Priority[value.upper()]
            elif key == "alignment":
                value = Alignment[value.upper()]
            elif key == "spacing":
                value = self.scaled(value)
            elif key == "size":
                value = Size(self.scaled(value[0]), self.scaled(value[1]))
            elif key == "opacity":
                value = clamp(float(value), 0.0, 1.0)
            setattr(self, key, value)

    def draw(self, renderer, asset_name, rect, alpha=None):
        # Mostly lives here because it's where I have access to the theme and the scale, not because it's a good place
        # for it to live.
        asset = self.theme.load_asset(asset_name)
        if alpha is None:
            alpha = self.alpha
        asset.render(renderer, rect, alpha=alpha, scale=self.scale)
