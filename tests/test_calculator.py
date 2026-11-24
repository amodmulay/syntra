import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from calculator import add, divide, integrate, multiply, sin, subtract


class TestCalculator(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)
        self.assertEqual(add(-1, 1), 0)

    def test_subtract(self):
        self.assertEqual(subtract(5, 3), 2)
        self.assertEqual(subtract(1, 3), -2)

    def test_multiply(self):
        self.assertEqual(multiply(2, 3), 6)
        self.assertEqual(multiply(-2, 3), -6)

    def test_divide(self):
        self.assertEqual(divide(6, 3), 2)
        self.assertEqual(divide(-6, 3), -2)
        with self.assertRaises(ZeroDivisionError):
            divide(1, 0)

    def test_integrate(self):
        self.assertAlmostEqual(integrate(lambda x: 3, 0, 2), 6, places=9)
        self.assertAlmostEqual(integrate(lambda x: x**2, 0, 1), 1 / 3, places=5)
        self.assertEqual(integrate(lambda x: x**2, 0, 1, n=1), 0.5)
        self.assertAlmostEqual(integrate(lambda x: x, 0, 2), 2.0, places=9)
        self.assertAlmostEqual(integrate(lambda x: x, 2, 0), -2.0, places=9)
        self.assertEqual(integrate(lambda x: x, 1, 1), 0)
        with self.assertRaises(ValueError):
            integrate(lambda x: x, 0, 1, n=0)
        with self.assertRaises(ValueError):
            integrate(lambda x: x, 0, 1, n=-5)

    def test_sin(self):
        cases = [
            (0, 0.0),
            (math.pi / 6, 0.5),
            (math.pi / 2, 1.0),
            (math.pi, 0.0),
            (-math.pi / 2, -1.0),
        ]
        for x, expected in cases:
            self.assertAlmostEqual(sin(x), expected, places=9)
            self.assertAlmostEqual(sin(x), math.sin(x), places=9)


if __name__ == "__main__":
    unittest.main()
