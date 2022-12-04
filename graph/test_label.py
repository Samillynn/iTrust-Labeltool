import unittest

from graph.label import Rectangle, Label, LabelType


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

"""
Tests behaviors of Label class.
"""
class TestLabel(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.label = Label(_type=LabelType.COMPONENT)

    def test_copy_properties(self):

        # test _type filed
        label_dict = {}
        self.label.copy_basic_properties(label_dict)
        self.assertEqual(self.label._type, LabelType.COMPONENT)

        label_dict = {'type': 'Databox'}
        self.label.copy_basic_properties(label_dict)
        self.assertEqual(self.label._type, LabelType.DATABOX)

        label_dict = {'type': 'Component'}
        self.label.copy_basic_properties(label_dict)
        self.assertEqual(self.label._type, LabelType.COMPONENT)