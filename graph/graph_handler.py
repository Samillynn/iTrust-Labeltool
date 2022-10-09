# noinspection PyPep8Naming
import logging

from handler_chain import HandlerChain
from observer import Observable
from .click_handler import UpdateLabelHandler, SelectDataboxHandler, AddConnectionHandler
# TODO: make end_point/start_point None after each time
from .cursor_handler import CursorHandler
from .drag_handler import DragHandlerChain, DuplicateLabelHandler, NewLabelHandler, MoveVertexHandler, MoveLabelHandler
from .image import Image
from .label import Label

logging.basicConfig(level=logging.INFO)


class GraphHandler(Observable, HandlerChain):

    def __init__(self, graph, image_path, labels=None):
        super().__init__()
        self.last_point = None
        self.current_point = None
        self.graph = graph
        self.cursor_handler = CursorHandler()

        self.labels = list(labels) if labels else []
        self.image = Image(image_path)

        self.on_drag = None
        self.init_on_drag()

        self.on_click = None
        self.init_on_click()

        self.state = None
        self.context = {}

        self.label_to_select_databox = None

        self.add_handler(self.handle_cursor)

    def init_on_drag(self):
        self.on_drag = DragHandlerChain()
        self.on_drag.add_handler(DuplicateLabelHandler(self))
        self.on_drag.add_handler(NewLabelHandler(self))
        self.on_drag.add_handler(MoveVertexHandler(self))
        self.on_drag.add_handler(MoveLabelHandler(self))

    def init_on_click(self):
        self.on_click = HandlerChain()
        self.on_click.add_handler(UpdateLabelHandler(self))
        self.on_click.add_handler(AddConnectionHandler(self))
        self.on_click.add_handler(SelectDataboxHandler(self))

    def add_label(self, label: Label):
        self.labels.append(label)

    def remove_label(self, label: Label):
        self.labels.remove(label)

    def start(self):
        self.notify_labels()
        self.notify_image()

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

    def _handle_cursor(self, event_type, values):

        self.current_point = values
        x, y = values

        if event_type == CursorHandler.HOVER:
            self.change_cursor_shape_by_cursor_position()
        elif event_type == CursorHandler.CLICK:
            self.on_click.handle(self.current_point)
        elif event_type == CursorHandler.DRAG_START:
            self.on_drag.start(self.current_point)
        elif event_type == CursorHandler.DRAG_HANDLE:
            self.on_drag.handle((x - self.last_point[0], y - self.last_point[1]))
        elif event_type == CursorHandler.DRAG_STOP:
            self.on_drag.stop()
        else:
            raise AssertionError(f'Unsupported cursor event type: {event_type}')

        self.last_point = (x, y)

    def handle_cursor(self, event, values):
        if not event.startswith('-GRAPH-'):
            return False

        for event_type, values in self.cursor_handler.handle(event, values):
            self._handle_cursor(event_type, values['-GRAPH-'])
        return True

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

    def draw_label(self, label):
        figure_id = self.graph.draw_rectangle(label.top_left, label.bottom_right,
                                              line_color="black", line_width=3)
        self.figures.append(figure_id)
        figure_id = self.graph.draw_text(f"{label.name}\n{label.category}\n{label.fullname}",
                                         location=label.center,
                                         color='black', font=("Courier New Bold", 10))
        self.figures.append(figure_id)

    def draw_line(self, label, conn):
        figure_id = self.graph.draw_line(label.center, conn.center)
        self.figures.append(figure_id)

    def draw(self, image=False):
        if image:
            self.graph.erase()
            self.graph.set_size(self.image.size)
            self.graph.draw_image(data=self.image.data, location=(-1, 1))

        for figure_id in self.figures:
            self.graph.delete_figure(figure_id)
        self.figures.clear()

        for label in self.labels:
            self.draw_label(label)
            for conn in label.connections:
                self.draw_line(label, conn)
