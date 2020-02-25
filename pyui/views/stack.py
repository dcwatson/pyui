from pyui.geom import Axis, Point, Rect, Size

from .base import Alignment, Priority, View


class Spacer(View):
    priority = Priority.OPTIONAL

    def content_size(self, available: Size):
        return Size(available.w, 0) if self.parent.axis == Axis.HORIZONTAL else Size(0, available.h)


class Stack(View):
    axis = None

    def __init__(self, *contents, alignment=Alignment.CENTER, spacing=10, **options):
        super().__init__(*contents, **options)
        self.cross = self.axis.cross
        self.alignment = alignment
        self.spacing = self.env.scaled(spacing)

    def minimum_size(self):
        """
        Returns the minimum size in each dimension of this view's content, not including any padding or borders.
        """
        main = self.spacing * (len(self.subviews) - 1)
        cross = 0
        for view in self.subviews:
            min_size = view.minimum_size()
            main += min_size[self.axis] + view.padding[self.axis] + view.border[self.axis]
            cross = max(cross, min_size[self.cross] + view.padding[self.cross] + view.border[self.cross])
        return self.axis.size(main, cross)

    def resize(self, available: Size):
        # https://kean.github.io/post/swiftui-layout-system
        # How much space along the layout axis we've allocated thus far.
        total = self.padding[self.axis] + self.border[self.axis] + (self.spacing * (len(self.subviews) - 1))
        # How much space along the layout axis we have remaining.
        # TODO: what to do when remaining < 0, i.e. no room for subviews?
        remaining = available[self.axis] - total
        # How much space is available on the cross axis.
        available_cross = available[self.cross] - self.padding[self.cross] - self.border[self.cross]
        # The maximum amount of space on the cross axis any subview occupies.
        max_cross = 0
        # Group our subviews by priority, and calculate the minimum total size along our axis for each group.
        groups = {}
        for view in self.subviews:
            min_size = view.minimum_size()
            groups.setdefault(view.priority, {"minimum": 0, "views": []})
            groups[view.priority]["minimum"] += min_size[self.axis] + view.padding[self.axis] + view.border[self.axis]
            groups[view.priority]["views"].append(view)
        # Starting with the highest priority views, offer them an even split of the remaining available space
        # along the layout axis, reserving enough space for the minimal sizes of all views with lower priority.
        for priority in sorted(groups, reverse=True):
            reserved = sum(groups[p]["minimum"] for p in groups if p < priority)
            views = groups[priority]["views"]
            for idx, view in enumerate(views):
                # Take the remaining unreserved space, and divide it by how many views are left in this group.
                # TODO: we could make sure we offer at least the view's minimal space, but that may be unnecessary.
                offer = self.axis.size(int((remaining - reserved) / (len(views) - idx)), available_cross)
                # Offer the view some amount of space, let it decide how much it wants.
                view.resize(offer)
                # TODO: should we verify this is less than or equal to what was offered?
                total += view.frame.size[self.axis]
                remaining -= view.frame.size[self.axis]
                max_cross = max(max_cross, view.frame.size[self.cross])
        self.frame.size = self.axis.size(total, max_cross + self.padding[self.cross] + self.border[self.cross])

    def reposition(self, inside: Rect):
        origin = inside.origin
        self.frame.origin = Point(
            inside.left + ((inside.width - self.frame.width) // 2),
            inside.top + ((inside.height - self.frame.height) // 2),
        )
        current = origin[self.axis] + self.padding.leading(self.axis) + self.border.leading(self.axis)
        # Align based on the content size without the padding and borders.
        inner = self.frame - self.padding - self.border
        for idx, view in enumerate(self.subviews):
            if idx > 0:
                current += self.spacing
            cross = inner.origin[self.cross] + int(
                self.alignment.value * (inner.size[self.cross] - view.frame.size[self.cross])
            )
            view.reposition(Rect(origin=self.axis.point(current, cross), size=view.frame.size))
            current += view.frame.size[self.axis]


class HStack(Stack):
    axis = Axis.HORIZONTAL


class VStack(Stack):
    axis = Axis.VERTICAL
