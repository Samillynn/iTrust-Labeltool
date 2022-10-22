import imp
import json
import os
import shutil
from pathlib import Path

import globl
import modifier_key
from base_classes import EventHandler
from config import config
from graph.graph_manager import GraphManager
from graph.label import LabelListSerializer, LabelType, Rectangle
from utils import sg, current_milli_time
from window_manager import WindowManager
from graph.label import LabelListSerializer, Label


class NewProjectEH(EventHandler):
    layout = [
        [sg.T('Location:'), sg.FolderBrowse(key='location', initial_folder=os.getcwd())],
        [sg.T('Project Name:'), sg.I(key='project_name')],
        [sg.T('Image to label'), sg.FileBrowse(key='image_path')],
        [sg.B('Create'), sg.B('Exit')]
    ]

    def handle(self):
        event, values = sg.Window('Create New Project', self.layout).read(close=True)
        if event in ['Create']:
            project_path = Path(values['location'], values['project_name'])
            # TODO: delete exist_ok
            project_path.mkdir(exist_ok=True)
            os.chdir(project_path)

            old_image_path = Path(values['image_path'])
            new_image_path = f'{current_milli_time()}-{old_image_path.name}'
            shutil.copyfile(old_image_path, new_image_path)
            session = {
                "image_path": new_image_path,
                "labels": []
            }
            json.dump(session, open('session.json', 'w+'))
            show_workspace()


class OpenProjectEH(EventHandler):
    def handle(self):
        path = sg.popup_get_folder('Select Project to Open', default_path=os.getcwd())
        if path is not None:
            os.chdir(path)
            show_workspace()


class ProjectMenuEH(EventHandler):
    layout = [[sg.B('Open Existing Project', key='open')],
              [sg.B('Create New Project', key='create')]
              ]

    def handle(self):
        window = sg.Window('iTrust', self.layout, finalize=True)
        window_manager = WindowManager(window)
        window_manager.register_handler('open', OpenProjectEH())
        window_manager.register_handler('create', NewProjectEH())
        window_manager.run(close=True)


# def export_eh(event, file_path):
#     def convert_label(label_dict):
#         top_left = label_dict.pop('top_left')
#         bottom_right = label_dict.pop('bottom_right')
#         rect = Rectangle(top_left, bottom_right)
#         label_dict['coordinate'] = rect.center
#         label_dict['width'] = rect.height
#         label_dict['length'] = rect.width

#         if label_dict.get('databox'):
#             label_dict['databox'] = Rectangle(label_dict['databox']['top_left'],
#                                               label_dict['databox']['bottom_right']).center
#             print(label_dict)
#         else:
#             label_dict['databox'] = []

#     labels = json.load(open('session.json', 'r'))['labels']
#     for label in labels:
#         convert_label(label)
#     json.dump(labels, open(file_path, 'w+'), indent=2)

def export_eh(event, file_path):
    def to_export_label_dict(label: Label):
        result = label.basic_properties
        result['coordinate'] = label.center
        if label.databox is not None:
            result['databox'] = list(label.databox.center)
        else:
            result['databox'] = []

        return result

    label_dicts = json.load(open('session.json', 'r'))['labels']
    labels = LabelListSerializer().deserialize(label_dicts)
    export_label_dicts = [
        to_export_label_dict(label)  for label in labels if label._type == LabelType.COMPONENT
    ]
    json.dump(export_label_dicts, open(file_path, 'w+'), indent=2)


class Workspace:
    def __init__(self, root_path='.'):
        self.window = sg.Window(layout=self.layout(), finalize=True, return_keyboard_events=True, resizable=True)
        self.root_path = root_path
        self.bind_keys()

    def bind_keys(self):
        self.window.bind('<Key-Control_L>', 'KeyDown-Control')
        self.window.bind('<Key-Control_R>', 'KeyDown-Control')

    @staticmethod
    def layout():
        return [
            [sg.Graph(
                canvas_size=(0, 0),
                graph_bottom_left=(-1, -1),
                graph_top_right=(1, 1),
                key="-GRAPH-",
                change_submits=True,  # mouse click events
                background_color='lightblue',
                drag_submits=True,
                motion_events=True,
                float_values=True,
                expand_x=False,
                expand_y=False)],
            [sg.Text(key='info', size=(60, 1)), sg.I(visible=False, enable_events=True, key='export-filename'),
             sg.SaveAs('Export', key='-EXPORT-', file_types=(('JSON file', '*.json'),),
                       target='export-filename'),
             sg.B('New', key='-NEW-'), sg.B('Open', key='-OPEN-'), sg.B('Show/Hide connections', key='connections')]
        ]


def toggle_connections(event, values):
    print(f'connection enable={globl.connection_view.enabled}.')
    globl.connection_view.enabled = not globl.connection_view.enabled


# Show workspace
def show_workspace(project_path=None):
    layout = [
        [sg.Graph(
            canvas_size=(0, 0),
            graph_bottom_left=(-1, -1),
            graph_top_right=(1, 1),
            key="-GRAPH-",
            change_submits=True,  # mouse click events
            background_color='lightblue',
            drag_submits=True,
            motion_events=True,
            float_values=True,
            expand_x=False,
            expand_y=False)],
        [sg.Text(key='info', size=(0, 0)), sg.I(visible=False, enable_events=True, key='export-filename'),
         sg.Text(key='info', size=(0, 0)), sg.I(visible=False, enable_events=True, key='export-conn-filename'),

         sg.SaveAs('Export', key='-EXPORT-', file_types=(('JSON file', '*.json'),),
                   target='export-filename'),

         sg.SaveAs('Export Connections', key='-EXPORT-CONN-', file_types=(('JSON file', '*.json'),),
                   target='export-conn-filename'),

         sg.B('New', key='-NEW-'), sg.B('Open', key='-OPEN-'), sg.B('Show/Hide Connections', key='-CONN-')]
    ]

    if project_path is not None:
        os.chdir(project_path)
    window = sg.Window("Workplace", layout, finalize=True, return_keyboard_events=True, resizable=True)
    window.bind('<Key-Control_L>', 'KeyDown-Control')
    window.bind('<Key-Control_R>', 'KeyDown-Control')

    window_manager = WindowManager(window)

    window_manager.register_handler('', modifier_key.listen)
    graph_manager = GraphManager(window['-GRAPH-'])
    window_manager.add_handler(graph_manager)

    def export_conn_eh(event, file_path):
        print("calling export_conn_eh")
        result = {}
        for label in graph_manager.handler.labels:
            key_format = config["export"]["connection"]["key_format"]
            val_format = config["export"]["connection"]["val_format"]
            key = key_format.format(**label.basic_properties)
            val = [val_format.format(**conn.basic_properties) for conn in label.connections]
            result[key] = val

        print(file_path, result)
        json.dump(result, open(file_path, 'w+'), indent=2)

    window_manager.register_handler('-NEW-', NewProjectEH())
    window_manager.register_handler('-OPEN-', OpenProjectEH())
    window_manager.register_handler('export-filename', export_eh)
    window_manager.register_handler('-CONN-', toggle_connections)
    window_manager.register_handler('export-conn-filename', export_conn_eh)
    window_manager.run()


if __name__ == '__main__':
    show_workspace('')
