from pyui.geom import Size

from .base import View


class Rectangle(View):
    def __init__(self, width=None, height=None):
        # TODO: make these Bindings
        self.width = self.env.scaled(width) if width else None
        self.height = self.env.scaled(height) if height else None
        super().__init__()

    def content_size(self, available):
        if self.width and self.height:
            return Size(self.width, self.height)
        elif self.width:
            return Size(self.width, available.h)
        elif self.height:
            return Size(available.w, self.height)
        return available
