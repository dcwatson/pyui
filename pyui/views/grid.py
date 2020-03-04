from pyui.geom import Alignment, Axis, Point, Rect, Size
from pyui.utils import chunked

from .base import View


class Flow(View):
    def __init__(self, *contents, alignment=Alignment.CENTER, spacing=10, flex=True, **options):
        super().__init__(*contents, **options)
        self.cross = self.axis.cross
        self.alignment = (alignment, alignment) if isinstance(alignment, Alignment) else alignment
        self.spacing = (spacing, spacing) if isinstance(spacing, int) else spacing
        self.flex = flex


class Grid(View):
    # A vertical Grid lays out items from left to right, flowing from top to bottom:
    #    1 2
    #    3 4
    #    5 6
    # A horizontal Grid lays out items from top to bottom, flowing from left to right:
    #    1 3 5
    #    2 4 6
    # You can think of this axis like a scroll axis.

    def __init__(
        self,
        *contents,
        alignment=Alignment.CENTER,
        spacing=10,
        num=None,
        size=None,
        axis=Axis.VERTICAL,
        flex=False,
        **options
    ):
        super().__init__(*contents, **options)
        self.axis = Axis(axis)
        self.cross = self.axis.cross
        self.alignment = (alignment, alignment) if isinstance(alignment, Alignment) else alignment
        self.spacing = (spacing, spacing) if isinstance(spacing, int) else spacing
        if num and size:
            raise ValueError("Specify either number per row/column, or size per cell, not both.")
        self.num = num
        self.size = self.env.scaled(size) if size else None
        self.flex = flex
        self.count = 0

    def reuse(self, other):
        self.axis = other.axis
        self.cross = other.cross
        self.alignment = other.alignment
        self.spacing = other.spacing
        self.num = other.num
        self.size = other.size
        self.flex = other.flex
        self.count = other.count
        return True

    def minimum_size(self):
        # Minimum size for a Grid is a single row/column (based on Axis).
        main = self.spacing[self.axis] * (len(self.subviews) - 1)
        cross = 0
        for view in self.subviews:
            min_size = view.minimum_size()
            main += min_size[self.axis] + view.env.padding[self.axis] + view.env.border[self.axis]
            cross = max(cross, min_size[self.cross] + view.env.padding[self.cross] + view.env.border[self.cross])
        return self.axis.size(main, cross)

    def cross_count(self, available: Size):
        if self.num:
            return self.num
        elif self.size:
            available_cross = available[self.cross] - self.env.padding[self.cross] - self.env.border[self.cross]
            return int((available_cross + self.spacing[self.cross]) / (self.size + self.spacing[self.cross]))
        else:
            # TODO: try to automatically determine?
            raise ValueError("Please specify num or size.")

    def resize(self, available: Size):
        available = self.env.constrain(available)
        self.count = self.cross_count(available)
        available_cross = (
            available[self.cross]
            - self.env.padding[self.cross]
            - self.env.border[self.cross]
            - ((self.count - 1) * self.spacing[self.cross])
        )
        main = self.env.padding[self.axis] + self.env.border[self.axis]
        offer = self.size if self.size and not self.flex else available_cross // self.count
        for idx, views in enumerate(chunked(self.subviews, self.count)):
            if idx > 0:
                main += self.spacing[self.axis]
            max_main = 0
            for view in views:
                view.resize(self.cross.size(offer, offer))
                max_main = max(max_main, view.frame.size[self.axis])
            main += max_main
        self.frame.size = self.axis.size(main, available[self.cross])

    def reposition(self, inside: Rect):
        self.frame.origin = Point(
            inside.left + max(0, (inside.width - self.frame.width) // 2),
            inside.top + max(0, (inside.height - self.frame.height) // 2),
        )
        main = self.frame.origin[self.axis] + self.env.padding.leading(self.axis) + self.env.border.leading(self.axis)
        for views in chunked(self.subviews, self.count):
            max_main = 0
            cross = (
                self.frame.origin[self.cross]
                + self.env.padding.leading(self.cross)
                + self.env.border.leading(self.cross)
            )
            for idx, view in enumerate(views):
                if idx > 0:
                    cross += self.spacing[self.cross]
                view.reposition(Rect(origin=self.axis.point(main, cross), size=view.frame.size,))
                cross += view.frame.size[self.cross]
                max_main = max(max_main, view.frame.size[self.axis])
            main += max_main + self.spacing[self.axis]
