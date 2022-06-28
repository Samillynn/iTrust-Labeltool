import json
import os
import shutil
from pathlib import Path


from event_handler import EventHandler
from graph_handler import GraphHandler
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


def show_workspace(project_path=None):
    layout = [[sg.Graph(
        canvas_size=(0, 0),
        graph_bottom_left=(-1, -1),
        graph_top_right=(1, 1),
        key="-GRAPH-",
        change_submits=True,  # mouse click events
        background_color='lightblue',
        drag_submits=True,
        float_values=True), ],
        [sg.Text(key='info', size=(60, 1)), sg.B('Export', key='-EXPORT-', file_types=(('JSON file', '*.json'),)),
         sg.B('New', key='-NEW-'), sg.B('Open', key='-OPEN-')]]

    if project_path is not None:
        os.chdir(project_path)
    window = sg.Window("Workplace", layout, finalize=True, return_keyboard_events=True)
    window_manager = WindowManager(window)

    graph_handler = GraphHandler.from_json(graph=window['-GRAPH-'], json_path='session.json')
    window_manager.register_handler('-GRAPH-', graph_handler)

    window_manager.register_handler('-NEW-', NewProjectEH())
    window_manager.register_handler('-OPEN-', OpenProjectEH())
    window_manager.run()


if __name__ == '__main__':
    show_workspace('.')
