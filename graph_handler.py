# noinspection PyPep8Naming
import logging

from base_classes import EventHandler
# TODO: make end_point/start_point None after each time
from cursor_handler import CursorHandler
from image import Image
from label import Label
from utils import sg

logging.basicConfig(level=logging.INFO)


class DragHandler:
    def __init__(self, graph_handler):
        self.graph_handler: GraphHandler = graph_handler

    def start(self, position):
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

    def start(self, position):
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

    def ask_label_info(self):
        event, values = new_label_dialog()
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


# noinspection PyMethodOverriding
class GraphHandler(EventHandler):

    def __init__(self, graph, image_path, labels=None):
        self.last_point = None
        self.current_point = None
        self.graph = graph
        self.cursor_handler = CursorHandler()

        self.labels = list(labels) if labels else []
        self.image = Image(image_path)
        self.observers = []

        self.drag_chain = DragHandlerChain()
        self.drag_chain.add_handler(NewLabelHandler(self))
        self.drag_chain.add_handler(MoveVertexHandler(self))
        self.drag_chain.add_handler(MoveLabelHandler(self))

    def add_label(self, label: Label):
        self.labels.append(label)

    def start(self):
        self.notify_labels()
        self.notify_image()

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify(self, event, values):
        for observer in self.observers:
            observer(event, values)

    def nearby_vertex(self, position):
        for label in self.labels:
            if vertex_name := label.nearby_vertex(position):
                return label, vertex_name

        return None

    def hovered_label(self, position):
        for label in self.labels:
            if label.includes(position):
                return label

        return None

    def notify_labels(self):
        self.notify('labels', self.labels)

    def notify_image(self):
        self.notify('image', self.image)

    def handle_cursor(self, event_type, values):
        self.current_point = values
        x, y = values

        if event_type == CursorHandler.HOVER:
            self.change_cursor_shape_by_cursor_position()
        elif event_type == CursorHandler.CLICK:
            self.process_click()
            self.notify_labels()
        elif event_type == CursorHandler.DRAG_START:
            self.drag_chain.start(self.current_point)
        elif event_type == CursorHandler.DRAG_HANDLE:
            self.drag_chain.handle((x - self.last_point[0], y - self.last_point[1]))
        elif event_type == CursorHandler.DRAG_STOP:
            self.drag_chain.stop()
        else:
            raise AssertionError(f'Unsupported cursor event type: {event_type}')

        self.last_point = (x, y)

    def react(self, event, values):
        if event in ['+', '-']:
            if event == '+':
                self.image.resize += 0.1
            elif event == '-':
                if self.image.resize >= 0.1:
                    self.image.resize -= 0.1
            return

        for event_type, values in self.cursor_handler.handle(event, values):
            self.handle_cursor(event_type, values)

    def change_cursor_shape_by_cursor_position(self):
        for label in self.labels:
            if label.nearby_vertex(self.current_point):
                self.graph.set_cursor("cross")
                break
            elif label.includes(self.current_point):
                self.graph.set_cursor("fleur")
                break
        else:
            self.graph.set_cursor("arrow")

    def process_click(self):
        if label := self.hovered_label(self.current_point):
            event, values = update_label_dialog(label)
            if event in ['Delete']:
                self.labels.remove(label)
            elif event in ['Update']:
                label.name = values['name']
                label.category = values['type']
                label.text = values['text']
            elif event in ['Cancel', None]:
                ...
            else:
                raise AssertionError(event)


DIALOG_OPTIONS = {
    'type': ['Big Tank', 'Small Tank', 'Pump', 'Dosing Pump', 'UV Dechlorinator', 'Filter', 'Other types']
}


def update_label_dialog(label):
    layout = base_dialog_layout(label)
    layout += [[sg.B('Update'), sg.Cancel(), sg.B('Delete', button_color='red')]]
    return sg.Window('Update label', layout).read(close=True)


def new_label_dialog():
    layout = base_dialog_layout()
    layout += [[sg.Submit(), sg.Exit()]]
    return sg.Window('Create new label', layout).read(close=True)


def base_dialog_layout(label=None):
    if label is None:
        label = Label()
    return [
        [sg.T('Name'), sg.I(label.name, key='name')],
        [sg.T('Type'), sg.DD(DIALOG_OPTIONS['type'], default_value=label.category, key='type')],
        [sg.T('Text'), sg.I(label.text, key='text')],
    ]


class GraphView:
    def __init__(self, graph):
        self.graph = graph
        self._image: Image = Image()
        self._labels: list[Label] = []
        self.figures: list[int] = []

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, image: Image):
        self._image = image
        self.draw(image=True)

    @property
    def labels(self):
        return self._labels

    @labels.setter
    def labels(self, labels: list[Label]):
        self._labels = labels
        self.draw(image=False)

    def draw(self, image=False):
        if image:
            self.graph.erase()
            self.graph.set_size(self.image.size)
            self.graph.draw_image(data=self.image.data, location=(-1, 1))
        for figure_id in self.figures:
            self.graph.delete_figure(figure_id)
        self.figures.clear()

        for label in self.labels:
            figure_id = self.graph.draw_rectangle(label.top_left, label.bottom_right,
                                                  line_color="black", line_width=3)
            self.figures.append(figure_id)
            figure_id = self.graph.draw_text(f"{label.name}\n{label.category}\n{label.text}",
                                             location=label.center,
                                             color='black', font=("Courier New Bold", 10))
            self.figures.append(figure_id)
