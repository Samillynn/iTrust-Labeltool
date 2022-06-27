# noinspection PyPep8Naming
import copy
import json
import logging
import os

import PySimpleGUI as sg

from utils import Coordinate, get_image_size, convert_to_bytes

logging.basicConfig(level=logging.INFO)


def get_label_info():
    return sg.Window('X', [[sg.T('Name'), sg.I(key='-NAME-')],
                           [sg.T('Type'),
                            sg.DD(['Big Tank', 'Small Tank', 'Pump', 'Dosing Pump', 'Other types'], key='-TYPE-')],
                           [sg.T('Parent'), sg.DD([f'Stage {i}' for i in range(1, 7)], key='-PARENT-')],
                           [sg.Submit(), sg.Exit()]]).read(close=True)


class GraphHandler:
    DIALOG_OPTIONS = {
        'type': ['Big Tank', 'Small Tank', 'Pump', 'Dosing Pump', 'UV Dechlorinator', 'Filter', 'Other types']
    }

    def __init__(self, graph, image_path, labels=None, save_to=None):
        self.dragging = False
        self.start_point = None
        self.end_point = None
        self.prior_rect = None
        self.save_to = save_to
        self.labels = list(labels) if labels else []

        self.image_path = image_path
        self.graph: sg.Graph = graph
        width, height = get_image_size(image_path)
        graph.set_size((width, height))

        self.render()

    @classmethod
    def from_json(cls, graph, json_path):
        logging.info(os.getcwd())
        session = json.load(open(json_path, 'r'))
        image_path = session['image_path']
        labels = session['labels']
        for label in labels:
            top_left = label.pop('top_left')
            bottom_right = label.pop('bottom_right')
            label['coordinate'] = Coordinate(top_left, bottom_right)
        return cls(graph, save_to=json_path, image_path=image_path, labels=labels)

    def process(self, event, values):
        x, y = values

        # TODO: drag inside existing labels should not trigger any action
        if not self.dragging:
            self.dragging = True
            self.start_point = (x, y)
        else:
            self.end_point = (x, y)

        if self.prior_rect:
            self.graph.delete_figure(self.prior_rect)
        if None not in (self.start_point, self.end_point):
            self.prior_rect = self.graph.draw_rectangle(self.start_point, self.end_point, line_color='red')

        if event.endswith('+UP'):
            self.dragging = False
            if self.start_point == self.end_point:
                self.process_click()
            else:
                self.process_drag()

            if self.save_to is not None:
                json.dump(self.to_json(), open(self.save_to, 'w+'))
            self.render()

    def process_click(self):
        for label in self.labels:
            if label["coordinate"].is_surrounding(self.end_point):
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

    def process_drag(self):
        event, values = self.new_label_dialog()
        if event in ['Submit']:
            logging.info(f'{self.start_point} {self.end_point}')
            self.labels.append(
                values | {"coordinate": Coordinate(self.start_point, self.end_point)})
        elif event in ['Exit', None]:
            pass
        else:
            raise AssertionError(event)

    def render(self):
        self.graph.erase()
        self.graph.draw_image(data=convert_to_bytes(self.image_path), location=(-1, 1))
        for label in self.labels:
            self.graph.draw_rectangle(label["coordinate"].top_left, label["coordinate"].bottom_right, line_color='red')
            self.graph.draw_text(f"{label['name']}\n({label['type']})", location=label["coordinate"].center,
                                 color='red')

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

