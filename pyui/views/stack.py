from pyui.geom import Axis, Point, Priority, Rect, Size

from .base import View


class Spacer(View):
    def __init__(self):
        super().__init__()
        self.priority(Priority.OPTIONAL)

    def content_size(self, available: Size):
        return Size(available.w, 0) if self.parent.axis == Axis.HORIZONTAL else Size(0, available.h)


class Stack(View):
    axis = None

    def __init__(self, *contents, alignment=None, spacing=None, **options):
        super().__init__(*contents, **options)
        self.cross = self.axis.cross
        if alignment is not None:
            self.alignment(alignment)
        if spacing is not None:
            self.spacing(spacing)

    def minimum_size(self):
        """
        Returns the minimum size in each dimension of this view's content, not including any padding or borders.
        """
        main = self.env.spacing * (len(self.subviews) - 1)
        cross = 0
        for view in self.subviews:
            min_size = view.minimum_size()
            main += min_size[self.axis] + view.env.padding[self.axis] + view.env.border[self.axis]
            cross = max(cross, min_size[self.cross] + view.env.padding[self.cross] + view.env.border[self.cross])
        return self.axis.size(main, cross)

    def resize(self, available: Size):
        # https://kean.github.io/post/swiftui-layout-system
        # How much space along the layout axis we've allocated thus far.
        total = self.env.padding[self.axis] + self.env.border[self.axis] + (self.env.spacing * (len(self.subviews) - 1))
        # How much space along the layout axis we have remaining.
        # TODO: what to do when remaining < 0, i.e. no room for subviews?
        available = self.env.constrain(available)
        remaining = available[self.axis] - total
        # How much space is available on the cross axis.
        available_cross = available[self.cross] - self.env.padding[self.cross] - self.env.border[self.cross]
        # The maximum amount of space on the cross axis any subview occupies.
        max_cross = 0
        # Group our subviews by priority, and calculate the minimum total size along our axis for each group.
        groups = {}
        mins = {}
        for view in self.subviews:
            min_size = view.minimum_size()
            mins[view] = min_size[self.axis] + view.env.padding[self.axis] + view.env.border[self.axis]
            groups.setdefault(view.env.priority, {"minimum": 0, "views": []})
            groups[view.env.priority]["minimum"] += mins[view]
            groups[view.env.priority]["views"].append(view)
        # Starting with the highest priority views, offer them an even split of the remaining available space
        # along the layout axis, reserving enough space for the minimal sizes of all views with lower priority.
        for priority in sorted(groups, reverse=True):
            reserved = sum(groups[p]["minimum"] for p in groups if p < priority)
            views = groups[priority]["views"]
            # TODO: sort views within a priority by whether they have fixed sizes?
            for idx, view in enumerate(views):
                # Take the remaining unreserved space, and divide it by how many views are left in this group.
                # Always offer at least the view's minimal space along the primary axis.
                offer = self.axis.size(
                    max(mins[view], int((remaining - reserved) / (len(views) - idx))), available_cross
                )
                # Offer the view some amount of space, let it decide how much it wants.
                view.resize(offer)
                # TODO: should we verify this is less than or equal to what was offered?
                total += view.frame.size[self.axis]
                remaining -= view.frame.size[self.axis]
                max_cross = max(max_cross, view.frame.size[self.cross])
        self.frame.size = self.axis.size(total, max_cross + self.env.padding[self.cross] + self.env.border[self.cross])

    def reposition(self, inside: Rect):
        self.frame.origin = Point(
            inside.left + max(0, (inside.width - self.frame.width) // 2),
            inside.top + max(0, (inside.height - self.frame.height) // 2),
        )
        current = (
            self.frame.origin[self.axis] + self.env.padding.leading(self.axis) + self.env.border.leading(self.axis)
        )
        # Align based on the content size without the padding and borders.
        inner = self.frame - self.env.padding - self.env.border
        for idx, view in enumerate(self.subviews):
            if idx > 0:
                current += self.env.spacing
            cross = inner.origin[self.cross] + int(
                self.env.alignment.value * (inner.size[self.cross] - view.frame.size[self.cross])
            )
            view.reposition(Rect(origin=self.axis.point(current, cross), size=view.frame.size))
            current += view.frame.size[self.axis]


class HStack(Stack):
    axis = Axis.HORIZONTAL


class VStack(Stack):
    axis = Axis.VERTICAL
