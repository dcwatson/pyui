from pyui.geom import Size

from .base import View


class Rectangle(View):
    def content_size(self, available: Size):
        return available
