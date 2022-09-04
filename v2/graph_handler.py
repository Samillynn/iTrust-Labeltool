# noinspection PyPep8Naming
import logging

from base_classes import EventHandler
from utils import sg, Rectangle, get_image_size, convert_to_bytes
# TODO: make end_point/start_point None after each time
from v2.cursor_handler import CursorHandler
from v2.label import Label

logging.basicConfig(level=logging.INFO)


class Image:
    def __init__(self, path: str = ''):
        self.path: str = path
        self._resize: float = 1

    def __repr__(self):
        return f'{type(self).__name__}({self.path})'

    @property
    def data(self) -> bytes:
        if self.path:
            return convert_to_bytes(self.path, self.size)
        else:
            return b''

    @property
    def resize(self):
        return self._resize

    @resize.setter
    def resize(self, value):
        if value < 0:
            raise ValueError(f'Resize ratio should be positive: {value}')
        else:
            self._resize = value

    @property
    def size(self) -> tuple[int, int]:
        width, height = get_image_size(self.path)
        return int(width * self.resize), int(height * self.resize)


# noinspection PyMethodOverriding
class GraphHandler(EventHandler):
    DIALOG_OPTIONS = {
        'type': ['Big Tank', 'Small Tank', 'Pump', 'Dosing Pump', 'UV Dechlorinator', 'Filter', 'Other types']
    }

    def __init__(self, graph, image_path, labels=None):
        self.is_new_label = False
        self.last_point = None
        self.current_label = None
        self.dragging = False
        self.start_point = None
        self.current_point = None
        self.graph = graph
        self.cursor_handler = CursorHandler()

        self.labels = list(labels) if labels else []
        self.image = Image(image_path)
        self.observers = []

    def start(self):
        self.update_labels()
        self.update_image()

    def register(self, observer):
        self.observers.append(observer)

    def update(self, event, values):
        for observer in self.observers:
            observer(event, values)

    def update_labels(self):
        self.update('labels', self.labels)

    def update_image(self):
        self.update('image', self.image)

    def handle_cursor(self, event_type, values):
        self.current_point = values
        x, y = values

        if event_type == CursorHandler.HOVER:
            self.change_cursor_shape_by_cursor_position()

        elif event_type == CursorHandler.CLICK:
            self.process_click()
            self.update_labels()

        elif event_type == CursorHandler.DRAG_START:
            for label in self.labels:
                if label.hold(self.current_point) is not None:
                    self.current_label = label
                    break
            else:
                self.is_new_label = True
                self.graph.set_cursor("cross")
                self.current_label = Label(self.current_point, self.current_point)
                self.current_label.hold(corner_id=Rectangle.TOP_LEFT)
                self.labels.append(self.current_label)

        elif event_type == CursorHandler.DRAG_HANDLE:
            self.current_label.drag(x - self.last_point[0], y - self.last_point[1])
            self.update_labels()

        elif event_type == CursorHandler.DRAG_STOP:
            self.current_label.release()
            if self.is_new_label:
                self.process_new_label()
                self.update_labels()
                self.is_new_label = False
                self.graph.set_cursor("arrow")
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
            if (corner_id := label.near(self.current_point)) is not None:
                if corner_id == Rectangle.CENTER:
                    self.graph.set_cursor("fleur")
                elif 1 <= corner_id <= 4:
                    self.graph.set_cursor("cross")
                else:
                    raise AssertionError
                break
        else:
            self.graph.set_cursor("arrow")

    def process_click(self):

        for label in self.labels:
            if label.includes(self.current_point):
                event, values = self.update_label_dialog(label)
                if event in ['Delete']:
                    self.labels.remove(label)
                    break
                elif event in ['Update']:
                    label.name = values['name']
                    label.category = values['type']
                    label.text = values['text']
                    break
                elif event in ['Cancel', None]:
                    break
                else:
                    raise AssertionError(event)

    def process_new_label(self):
        event, values = self.new_label_dialog()
        if event in ['Submit']:
            logging.info(f'{self.start_point} {self.current_point}')
            self.current_label.name = values['name']
            self.current_label.category = values['type']
            self.current_label.text = values['text']
        elif event in ['Exit', None]:
            self.labels.remove(self.current_label)
            pass
        else:
            raise AssertionError(event)

    def update_label_dialog(self, label):
        layout = self.base_dialog_layout(label)
        layout += [[sg.B('Update'), sg.Cancel(), sg.B('Delete', button_color='red')]]
        return sg.Window('Update label', layout).read(close=True)

    def new_label_dialog(self):
        layout = self.base_dialog_layout()
        layout += [[sg.Submit(), sg.Exit()]]
        return sg.Window('Create new label', layout).read(close=True)

    def base_dialog_layout(self, label=None):
        if label is None:
            label = Label()
        return [
            [sg.T('Name'), sg.I(label.name, key='name')],
            [sg.T('Type'), sg.DD(self.DIALOG_OPTIONS['type'], default_value=label.category, key='type')],
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
