import copy
from typing import TYPE_CHECKING

import modifier_key
from pair_property import global_pair_property, create_new_pair, assign_current_choice
from utils import sg
from .dialog import BaseDialog
from .label import Label, LabelSerializer

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
        self.dialog = None
        super().__init__(graph_handler)

    def start(self, position):
        # if self.graph_handler.hovered_label(position) or self.graph_handler.nearby_vertex(position):
        if self.graph_handler.hovered_label(position):
            return False

        self.label = Label(position, position)
        self.dialog = BaseDialog(self.label)
        self.graph_handler.add_label(self.label)

        self.graph_handler.graph.set_cursor("cross")
        return True

    def handle(self, displacement):
        self.label.move_vertex('bottom_right', displacement)
        self.graph_handler.notify_labels()

    def stop(self):
        self.label.parent_component_name = self.graph_handler.pair_parent_name
        self.label._type = self.graph_handler.pair_type

        self.ask_label_info()
        self.graph_handler.notify_labels()
        self.graph_handler.graph.set_cursor('arrow')

        self.label = None

        if global_pair_property.current_choice is not None:
             create_new_pair()

    def component_layout(self):
        base_dialog = BaseDialog()
        layout = [
            base_dialog.layout_flip(),
            base_dialog.layout_rotation(),
            [sg.T("Parent"), sg.I(key='parent', default_text=global_pair_property.name)],
            [sg.T("Coordinate"), sg.T(
                f"x: {self.label.center_x}; y: {self.label.center_y}")],
            [sg.Submit(), sg.Exit()]
        ]

        return layout

    def component_dialog(self):
        self.dialog.create('Component', self.component_layout())
        return self.dialog.read(close=True)

    def databox_layout(self):
        layout = [
            [sg.T("Parent"), sg.I(key='parent', default_text=global_pair_property.name)],
            [sg.T("Coordinate"), sg.T(
                f"x: {self.label.center_x}; y: {self.label.center_y}")],
            [sg.Submit(), sg.Exit()]
        ]

        return layout

    def databox_dialog(self):
        self.dialog.create('Databox', self.databox_layout())
        return self.dialog.read(close=True)

    def new_label_dialog(self):
        layout = self.dialog.layout(enable_event=False)
        layout += [[sg.Submit(), sg.Exit()]]
        self.dialog.create('Create new label', layout)
        return self.dialog.read(close=True)

    def ask_label_info(self):

        # whether a component or a databox is currently labeled
        current_choice = global_pair_property.current_choice

        if current_choice is None:
            event, values = self.new_label_dialog()
        elif current_choice == 'Component':
            event, values = self.component_dialog()
        elif current_choice == "Databox":
            event, values = self.databox_dialog()
        else:
            raise AssertionError

        if event in ['Submit']:
            self.label.copy_basic_properties(values)
            if global_pair_property.current_choice is not None:
                 assign_current_choice(self.label)
        elif event in ['Exit', None]:
            self.graph_handler.labels.remove(self.label)
            if global_pair_property.current_choice is not None:
                assign_current_choice(None)
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
        if self.graph_handler.hovered_label(position):
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
