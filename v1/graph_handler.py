# noinspection PyPep8Naming
import copy
import json
import logging
import os

from event_handler import EventHandler
from utils import sg, Rectangle, get_image_size, convert_to_bytes, near

# TODO: make end_point/start_point None after each time

logging.basicConfig(level=logging.INFO)


def get_label_info():
    return sg.Window('X', [[sg.T('Name'), sg.I(key='-NAME-')],
                           [sg.T('Type'),
                            sg.DD(['Big Tank', 'Small Tank', 'Pump', 'Dosing Pump', 'Other types'], key='-TYPE-')],
                           [sg.T('Parent'), sg.DD([f'Stage {i}' for i in range(1, 7)], key='-PARENT-')],
                           [sg.Submit(), sg.Exit()]]).read(close=True)


# noinspection PyMethodOverriding
class GraphHandler(EventHandler):
    DIALOG_OPTIONS = {
        'type': ['Big Tank', 'Small Tank', 'Pump', 'Dosing Pump', 'UV Dechlorinator', 'Filter', 'Other types']
    }

    def __init__(self, graph, image_path, labels=None, save_to=None):
        self.figure_ids = []
        self.is_new_label = False
        self.last_point = None
        self.current_label = None
        self.dragging = False
        self.start_point = None
        self.current_point = None
        self.prior_rect = None
        self.save_to = save_to
        self.labels = list(labels) if labels else []

        self.image_path = image_path
        self.graph: sg.Graph = graph

        self.render(draw_image=True)

    @classmethod
    def from_json(cls, graph, json_path):
        logging.info(os.getcwd())
        session = json.load(open(json_path, 'r'))
        image_path = session['image_path']
        labels = session['labels']
        for label in labels:
            top_left = label.pop('top_left')
            bottom_right = label.pop('bottom_right')
            label['coordinate'] = Rectangle(top_left, bottom_right)
        return cls(graph, save_to=json_path, image_path=image_path, labels=labels)

    def react(self, event, values):
        self.current_point = values
        x, y = values

        if event.endswith('+MOVE'):
            self.change_cursor_shape_by_cursor_position()
            return
        if not self.dragging:
            self.dragging = True
            self.start_point = (x, y)
            for label in self.labels:
                if label["coordinate"].hold(self.start_point) is not None:
                    self.current_label = label
                    break
            else:
                self.is_new_label = True
                self.graph.set_cursor("cross")
                self.current_label = {"coordinate": Rectangle(self.start_point, self.start_point), "name": '',
                                      "type": '', "label": '', "text": ''}
                self.current_label["coordinate"].hold(corner_id=Rectangle.TOP_LEFT)
                self.labels.append(self.current_label)
        else:
            self.current_label["coordinate"].drag(x - self.last_point[0], y - self.last_point[1])

        if event.endswith('+UP'):
            self.dragging = False
            self.current_label["coordinate"].release()
            if near(self.start_point, self.current_point, 0.005):
                if self.is_new_label:
                    self.labels.remove(self.current_label)
                self.process_click()
            elif self.is_new_label:
                self.process_new_label()
                self.is_new_label = False
                self.graph.set_cursor("arrow")

            if self.save_to is not None:
                json.dump(self.to_json(), open(self.save_to, 'w+'), indent=2)

        self.last_point = (x, y)
        self.render()

    def change_cursor_shape_by_cursor_position(self):
        for label in self.labels:
            if (corner_id := label["coordinate"].near(self.current_point)) is not None:
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
            if label["coordinate"].includes(self.current_point):
                event, values = self.update_label_dialog(label)
                if event in ['Delete']:
                    self.labels.remove(label)
                    break
                elif event in ['Update']:
                    label |= values
                    break
                elif event in ['Cancel', None]:
                    break
                else:
                    raise AssertionError(event)

    def process_new_label(self):
        event, values = self.new_label_dialog()
        if event in ['Submit']:
            logging.info(f'{self.start_point} {self.current_point}')
            self.current_label |= values
        elif event in ['Exit', None]:
            self.labels.remove(self.current_label)
            pass
        else:
            raise AssertionError(event)

    def render(self, draw_image=False):
        # clear graph for next render
        if draw_image:
            self.graph.erase()
            width, height = get_image_size(self.image_path)
            self.graph.set_size((width, height))
            self.graph.draw_image(data=convert_to_bytes(self.image_path), location=(-1, 1))
        for figure_id in self.figure_ids:
            self.graph.delete_figure(figure_id)
        self.figure_ids.clear()

        for label in self.labels:
            figure_id = self.graph.draw_rectangle(label["coordinate"].top_left, label["coordinate"].bottom_right,
                                                  line_color="black", line_width=3)
            self.figure_ids.append(figure_id)
            figure_id = self.graph.draw_text(f"{label['name']}\n{label['type']}\n{label['text']}", location=label["coordinate"].center,
                                             color='black', font=("Courier New Bold", 10))
            self.figure_ids.append(figure_id)

    def update_label_dialog(self, label):
        layout = self.base_dialog_layout(label)
        layout += [[sg.B('Update'), sg.Cancel(), sg.B('Delete', button_color='red')]]
        return sg.Window('Update label', layout).read(close=True)

    def new_label_dialog(self):
        layout = self.base_dialog_layout()
        layout += [[sg.Submit(), sg.Exit()]]
        return sg.Window('Create new label', layout).read(close=True)

    def base_dialog_layout(self, label=None):
        dialog_info = {'name': '', 'type': '', 'label': '', 'text': ''}
        if label is None:
            label = dialog_info
        return [
            [sg.T('Name'), sg.I(label['name'], key='name')],
            [sg.T('Type'), sg.DD(self.DIALOG_OPTIONS['type'], default_value=label['type'], key='type')],
            [sg.T('Label'), sg.I(label['label'], key='label')],
            [sg.T('Text'), sg.I(label['text'], key='text')],
        ]

    def to_json(self):
        labels = copy.deepcopy(self.labels)
        for label in labels:
            coordinate = label.pop('coordinate')
            label['top_left'] = coordinate.top_left
            label['bottom_right'] = coordinate.bottom_right
        return {"image_path": self.image_path, "labels": labels}
