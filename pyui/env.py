from .theme import Theme


class Env:
    def __init__(self, default=None):
        self.name = None
        self.default = default

    def __get__(self, instance, owner=None):
        if not instance:
            return self
        if self.name not in instance.__dict__:
            # TODO: search parents
            # parent = instance.__dict__['parent']
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

    def __init__(self):
        self.parent = None

    def inherit(self, parent):
        self.parent = parent

    def scaled(self, value):
        return value.__class__(value * self.scale)
