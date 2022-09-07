import unittest

from graph.label import Rectangle


class RectangleTest(unittest.TestCase):
    def setUp(self) -> None:
        self.rectangle = Rectangle()

    def test_move(self):
        self.rectangle.move((5.2, 13.14))
        self.assertEqual(self.rectangle.top_left, (5.2, 13.14))

    def test_move_vertex(self):
        self.rectangle.move_vertex('bottom_right', (5.2, 13.14))
        self.assertEqual(self.rectangle.top_right, (5.2, 0))
        self.assertEqual(self.rectangle.bottom_left, (0, 13.14))

    def test_move_vertex_by_property(self):
        self.rectangle.bottom_right = 5.2, 13.14
        self.assertEqual(self.rectangle.top_right, (5.2, 0))
        self.assertEqual(self.rectangle.bottom_left, (0, 13.14))
