from pyui.geom import Size

from .base import View


class Rectangle(View):
    def __init__(self, width=1.0, height=1.0):
        # TODO: make these Bindings
        self.width = self.env.scaled(width) if isinstance(width, int) else width
        self.height = self.env.scaled(height) if isinstance(height, int) else height
        super().__init__()

    def content_size(self, available):
        w = self.width if isinstance(self.width, int) else int(self.width * available.w)
        h = self.height if isinstance(self.height, int) else int(self.height * available.h)
        return Size(w, h)
