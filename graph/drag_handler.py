import copy
from typing import TYPE_CHECKING

import modifier_key
from utils import sg
from .dialog import base_dialog_layout
from .label import Label

if TYPE_CHECKING:
    from .graph_handler import GraphHandler


class DragHandler:
    def __init__(self, graph_handler):
        self.graph_handler: GraphHandler = graph_handler

    def start(self, position) -> bool:
        return False

    def handle(self, displacement):
        ...

    def stop(self):
        ...


class DragHandlerChain:
    def __init__(self):
        self.handlers: list[DragHandler] = []
        self.active_handler: DragHandler | None = None

    def add_handler(self, handler: DragHandler):
        self.handlers.append(handler)

    def start(self, position) -> bool:
        for handler in self.handlers:
            if handler.start(position):
                self.active_handler = handler
                return True
        return False

    def handle(self, displacement):
        assert self.active_handler is not None
        self.active_handler.handle(displacement)

    def stop(self):
        assert self.active_handler is not None
        self.active_handler.stop()

        self.active_handler = None


class NewLabelHandler(DragHandler):
    def __init__(self, graph_handler):
        self.label = None
        super().__init__(graph_handler)

    def start(self, position):
        if self.graph_handler.hovered_label(position) or self.graph_handler.nearby_vertex(position):
            return False

        self.label = Label(position, position)
        self.graph_handler.add_label(self.label)

        self.graph_handler.graph.set_cursor("cross")
        return True

    def handle(self, displacement):
        self.label.move_vertex('bottom_right', displacement)
        self.graph_handler.notify_labels()

    def stop(self):
        self.ask_label_info()
        self.graph_handler.notify_labels()
        self.graph_handler.graph.set_cursor('arrow')

        self.label = None

    @staticmethod
    def new_label_dialog():
        layout = base_dialog_layout()
        layout += [[sg.Submit(), sg.Exit()]]
        return sg.Window('Create new label', layout).read(close=True)

    def ask_label_info(self):
        event, values = self.new_label_dialog()
        if event in ['Submit']:
            self.label.name = values['name']
            self.label.category = values['type']
            self.label.text = values['text']
        elif event in ['Exit', None]:
            self.graph_handler.labels.remove(self.label)
            pass
        else:
            raise AssertionError(event)


class MoveLabelHandler(DragHandler):
    def __init__(self, graph_handler):
        super().__init__(graph_handler)
        self.label = None

    def start(self, position):
        if label := self.graph_handler.hovered_label(position):
            self.label = label
            return True

        return False

    def handle(self, displacement):
        self.label.move(displacement)
        self.graph_handler.notify_labels()


class MoveVertexHandler(DragHandler):
    def __init__(self, graph_handler):
        super().__init__(graph_handler)
        self.label = None
        self.vertex_name = ''

    def start(self, position):
        if nearby := self.graph_handler.nearby_vertex(position):
            self.label, self.vertex_name = nearby
            return True

        return False

    def handle(self, displacement):
        self.label.move_vertex(self.vertex_name, displacement)
        self.graph_handler.notify_labels()


class DuplicateLabelHandler(DragHandler):
    def __init__(self, graph_handler):
        self.label = None
        super().__init__(graph_handler)

    def start(self, position):
        if (label := self.graph_handler.hovered_label(position)) and modifier_key.ctrl:
            self.label = copy.deepcopy(label)
            self.graph_handler.add_label(self.label)
            return True

        return False

    def handle(self, displacement):
        self.label.move(displacement)
        self.graph_handler.notify_labels()
