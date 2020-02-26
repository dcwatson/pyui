import sdl2

from pyui.geom import Alignment, Insets, Priority

from .theme import Theme


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
    theme = Env(default=Theme("themes/dark/config.json"))
    scale = Env(default=1.0)

    font = Env(default="default")
    font_size = Env()
    text_shadow = Env()
    color = Env(default=sdl2.SDL_Color(0, 0, 0))
    background = Env()
    radius = Env(default=0)
    padding = Env(default=Insets(0))
    border = Env(default=Insets(0))
    priority = Env(default=Priority.NORMAL)
    alignment = Env(default=Alignment.CENTER)
    spacing = Env(default=0)

    def __init__(self, class_name=None, **overrides):
        self.parent = None
        if class_name:
            self.load(class_name)
        for key, value in overrides.items():
            setattr(self, key, value)

    def inherit(self, parent):
        self.parent = parent

    def scaled(self, value):
        return value.__class__(value * self.scale)

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
            setattr(self, key, value)
