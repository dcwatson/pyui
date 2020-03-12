import unittest

from pyui.env import Environment
from pyui.font import Font
from pyui.geom import Insets, Point, Rect, Size
from pyui.utils import enumerate_last


class MeasurementTests(unittest.TestCase):
    def test_rect_insets(self):
        r1 = Rect(origin=(100, 100), size=(150, 50))
        r2 = r1 + Insets(10)
        self.assertEqual(r2.origin, Point(90, 90))
        self.assertEqual(r2.size, Size(170, 70))
        r3 = r1 - Insets(10)
        self.assertEqual(r3.origin, Point(110, 110))
        self.assertEqual(r3.size, Size(130, 30))

    def test_enumerate_last(self):
        values = list(enumerate_last([100, 200, 300]))
        self.assertEqual(values, [(0, 100, False), (1, 200, False), (2, 300, True)])
        self.assertEqual(list(enumerate_last([])), [])


class FontTests(unittest.TestCase):
    def test_font_word_breaking(self):
        font = Font.load("fonts/dejavu/DejaVuSans.ttf", 16)
        text = "hello world\nline\vtwo line-break"
        data = list(font.words(text))
        expected = [
            (0, 5, 38),  # hello
            (5, 6, 5),  # space
            (6, 11, 44),  # world
            (11, 12, 0),  # newline
            (12, 16, 28),  # line
            (17, 20, 29),  # two
            (20, 21, 5),  # space
            (21, 26, 34),  # line-
            (26, 31, 47),  # break
        ]
        self.assertEqual(data, expected)


class EnvironmentTests(unittest.TestCase):
    def test_inheritance(self):
        parent = Environment(font_size=24)
        child = Environment()
        self.assertEqual(child.font_size, Environment.font_size.default)
        child.inherit(parent)
        self.assertEqual(child.font_size, 24)


if __name__ == "__main__":
    Font.initialize(1.0)
    unittest.main()
