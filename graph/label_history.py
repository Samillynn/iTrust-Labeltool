import copy
import logging
from typing import Collection

from logdecorator import log_on_start, log_on_end

from graph.label import Label


class LabelHistory:
    def __init__(self):
        self.states = []
        self.current_index = -1

    def add_state(self, labels: Collection[Label]):
        return
        self.states = self.states[:self.current_index + 1]
        self.states.append(copy.deepcopy(labels))
        self.current_index += 1
        print('add', self.current_index)

    @property
    def current_state(self):
        return self.states[self.current_index]

    @log_on_end(logging.INFO, 'undo: {result}')
    def undo(self) -> Collection[Label] | None:
        if self.current_index <= 0:
            return None

        self.current_index -= 1
        print(self.current_index)
        return self.current_state

    @log_on_end(logging.INFO, 'redo: {result}')
    def redo(self) -> Collection[Label] | None:
        if self.current_index == len(self.states) - 1:
            return None

        self.current_index += 1
        return self.current_state
