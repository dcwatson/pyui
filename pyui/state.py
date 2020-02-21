class State:
    def __init__(self, python_type=None, default=None):
        self.python_type = python_type
        self.multi = False
        self.name = None
        self.default = default

    def __get__(self, instance, owner):
        if not instance:
            return self
        if self.name not in instance.__dict__:
            value = self.get_default()
            # Set the default value the first time it's accessed, so it's not changing on every access.
            self.__set__(instance, value)
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        instance.__dict__[self.name] = self.check_value(instance, value)
        instance.state_changed(self.name, value)

    def __set_name__(self, owner, name):
        self.name = name

    def get_default(self):
        return self.default() if callable(self.default) else self.default

    def check_value(self, instance, value):
        if value is None or self.python_type is None or isinstance(value, self.python_type):
            return value
        raise AttributeError(
            "{}.{} must be of type {} (got {})".format(
                instance.__class__.__name__, self.name, self.python_type.__name__, value.__class__.__name__
            )
        )
