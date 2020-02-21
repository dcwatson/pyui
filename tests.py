import unittest

from pyui.geom import Insets, Point, Rect, Size


class MeasurementTests(unittest.TestCase):
    def test_rect_insets(self):
        r1 = Rect(origin=(100, 100), size=(150, 50))
        r2 = r1 + Insets(10)
        self.assertEqual(r2.origin, Point(90, 90))
        self.assertEqual(r2.size, Size(170, 70))
        r3 = r1 - Insets(10)
        self.assertEqual(r3.origin, Point(110, 110))
        self.assertEqual(r3.size, Size(130, 30))


if __name__ == "__main__":
    unittest.main()
