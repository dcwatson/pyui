from .geom import Point, Rect, Size
from .utils import clamp


def linear(t):
    return t


def quadratic(t):
    return t * t


def bezier(t):
    return t * t * (3.0 - (2.0 * t))


def parametric(t):
    t2 = t * t
    return t2 / (2.0 * (t2 - t) + 1.0)


class Animation:
    def __init__(self, curve, duration=0.15):
        self.curve = curve
        self.duration = duration
        self.t = 0.0

    def interpolate(self, dt):
        self.t += dt
        return self.curve(clamp(self.t / self.duration, 0.0, 1.0))

    def step(self, dt):
        pass

    def finished(self):
        return self.t >= self.duration


class FrameAnimation(Animation):
    def __init__(self, old_value, new_value, modifier, curve=linear, duration=0.2):
        super().__init__(curve, duration)
        self.old_value = old_value.copy()
        self.new_value = new_value.copy()
        self.modifier = modifier

    def step(self, dt):
        pct = self.interpolate(dt)
        dx = self.new_value.left - self.old_value.left
        dy = self.new_value.top - self.old_value.top
        dw = self.new_value.width - self.old_value.width
        dh = self.new_value.height - self.old_value.height
        self.modifier(
            Rect(
                origin=Point(self.old_value.left + round(dx * pct), self.old_value.top + round(dy * pct)),
                size=Size(self.old_value.width + round(dw * pct), self.old_value.height + round(dh * pct)),
            )
        )
