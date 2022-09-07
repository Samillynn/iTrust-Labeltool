import unittest

from image import CoordinateTransfer


class TestCoordinateTransfer(unittest.TestCase):
    def test_to_absolute_center(self):
        coordinate_transfer = CoordinateTransfer((-1, -1), (1, 1), (500, 1000))
        self.assertEqual(
            coordinate_transfer.to_absolute((0, 0)),
            (250, 500)
        )

    def test_to_absolute_float(self):
        coordinate_transfer = CoordinateTransfer((-1, -1), (1, 1), (50, 100))
        self.assertEqual(
            coordinate_transfer.to_absolute((0.11, -0.33)),
            (27, 66)
        )
