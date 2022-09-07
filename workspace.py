import json
import os
import shutil
from pathlib import Path

import modifier_key
from base_classes import EventHandler
from graph.graph_handler import GraphHandler, GraphView
from graph.label import LabelSerializer, Rectangle, Label
from session_storage import JsonSessionStorage
from utils import sg, current_milli_time
from window_manager import WindowManager


class NewProjectEH(EventHandler):
    layout = [
        [sg.T('Location:'), sg.FolderBrowse(key='location', initial_folder=os.getcwd())],
        [sg.T('Project Name:'), sg.I(key='project_name')],
        [sg.T('Image to label'), sg.FileBrowse(key='image_path')],
        [sg.B('Create'), sg.B('Exit')]
    ]

    def react(self):
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
    def react(self):
        path = sg.popup_get_folder('Select Project to Open', default_path=os.getcwd())
        if path is not None:
            os.chdir(path)
            show_workspace()


class ProjectMenuEH(EventHandler):
    layout = [[sg.B('Open Existing Project', key='open')],
              [sg.B('Create New Project', key='create')]
              ]

    def react(self):
        window = sg.Window('iTrust', self.layout, finalize=True)
        window_manager = WindowManager(window)
        window_manager.register_handler('open', OpenProjectEH())
        window_manager.register_handler('create', NewProjectEH())
        window_manager.run(close=True)


def export_eh(event, file_path):
    def convert_label(label_dict):
        top_left = label_dict.pop('top_left')
        bottom_right = label_dict.pop('bottom_right')
        label_dict['coordinate'] = Rectangle(top_left, bottom_right).center
        if label_dict.get('databox'):
            convert_label(label_dict['databox'])
            print(label_dict)

    labels = json.load(open('session.json', 'r'))['labels']
    for label in labels:
        convert_label(label)
    json.dump(labels, open(file_path, 'w+'), indent=2)


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
        [sg.Text(key='info', size=(60, 1)), sg.I(visible=False, enable_events=True, key='export-filename'),
         sg.SaveAs('Export', key='-EXPORT-', file_types=(('JSON file', '*.json'),),
                   target='export-filename'),
         sg.B('New', key='-NEW-'), sg.B('Open', key='-OPEN-')]
    ]

    if project_path is not None:
        os.chdir(project_path)
    window = sg.Window("Workplace", layout, finalize=True, return_keyboard_events=True, resizable=True)
    window.bind('<Key-Control_L>', 'KeyDown-Control')
    window.bind('<Key-Control_R>', 'KeyDown-Control')

    window.bind("<Control-equal>", "-GRAPH-+")
    window.bind("<Control-KeyRelease-equal>", "Release-=")
    window.bind("<Control-minus>", "-GRAPH--")
    window.bind("<Control-KeyRelease-minus>", "Release--")

    window_manager = WindowManager(window)

    storage = JsonSessionStorage('session.json', LabelSerializer())
    graph_handler = GraphHandler(graph=window['-GRAPH-'], image_path=storage.image_path, labels=storage.labels)
    graph_view = GraphView(window['-GRAPH-'])

    def update_graph_view(event, values):
        if event == 'labels':
            labels = values
            graph_view.labels = labels

        elif event == 'image':
            image = values
            graph_view.image = image

    def update_graph_storage(event, values):
        if event == 'labels':
            labels = values
            storage.labels = labels

        elif event == 'image':
            image = values
            storage.image = image

    graph_handler.add_observer(update_graph_view)
    graph_handler.add_observer(update_graph_storage)
    graph_handler.start()

    window_manager.register_handler('', modifier_key.listen)
    window_manager.register_handler('-GRAPH-', graph_handler)

    window_manager.register_handler('-NEW-', NewProjectEH())
    window_manager.register_handler('-OPEN-', OpenProjectEH())
    window_manager.register_handler('export-filename', export_eh)
    window_manager.run()


if __name__ == '__main__':
    show_workspace('')
