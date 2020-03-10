import math

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


def spring(mass=1.0, stiffness=100.0, damping=10.0, velocity=0):
    # Ported from https://webkit.org/demos/spring/
    w0 = math.sqrt(stiffness / mass)
    zeta = damping / (2.0 * math.sqrt(stiffness * mass))
    if zeta < 1.0:
        wd = w0 * math.sqrt(1 - zeta * zeta)
        A = 1.0
        B = (zeta * w0 - velocity) / wd
    else:
        wd = 0.0
        A = 1.0
        B = w0 - velocity

    def solve(t):
        if zeta < 1.0:
            t = math.exp(-t * zeta * w0) * (A * math.cos(wd * t) + B * math.sin(wd * t))
        else:
            t = (A + B * t) * math.exp(-t * w0)
        return 1 - t

    return solve


class Animation:
    def __init__(self, curve, duration=0.15, delay=0.0):
        self.curve = curve
        self.duration = duration
        self.delay = delay

    def interpolate(self, t):
        return self.curve(clamp((t - self.delay) / self.duration, 0.0, 1.0))

    def finished(self, t):
        return t >= (self.duration + self.delay)

    def __call__(self, old_value, new_value, modifier):
        return AnimationExecutor(self, old_value, new_value, modifier)


class AnimationExecutor:
    def __init__(self, animation, old_value, new_value, modifier):
        self.animation = animation
        self.old_value = old_value.copy()
        self.new_value = new_value.copy()
        self.modifier = modifier
        self.t = 0.0

    def step(self, dt):
        self.t += dt
        pct = self.animation.interpolate(self.t)
        value = self.old_value.interpolate(self.new_value, pct)
        self.modifier(value)

    def finished(self):
        return self.animation.finished(self.t)
