import unittest

from graph.label_history import LabelHistory


class TestLabelHistory(unittest.TestCase):
    def setUp(self) -> None:
        self.label_history = LabelHistory()
        for i in range(5):
            self.label_history.add_state(i)

    def test_current_state(self):
        self.assertEqual(self.label_history.current_state, 4)

    def test_undo(self):
        self.assertEqual(self.label_history.undo(), 3)
        self.assertEqual(self.label_history.undo(), 2)
        self.assertEqual(self.label_history.undo(), 1)

    def test_redo(self):
        self.label_history.undo()
        self.label_history.undo()
        self.assertEqual(self.label_history.redo(), 3)
        self.assertEqual(self.label_history.redo(), 4)

    def test_add_state_after_undo(self):
        self.label_history.undo()
        self.label_history.undo()
        self.label_history.add_state(10)
        self.assertEqual(self.label_history.current_state, 10)
        self.assertEqual(self.label_history.undo(), 2)


