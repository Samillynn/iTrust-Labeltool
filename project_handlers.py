import json
import os
import shutil
import time
from pathlib import Path

import PySimpleGUI as sg

from window_manager import WindowManager
import workspace


def current_milli_time():
    return round(time.time() * 1000)


class NewProjectHandler:
    layout = [
        [sg.T('Location:'), sg.FolderBrowse(key='location', initial_folder=os.getcwd())],
        [sg.T('Project Name:'), sg.I(key='project_name')],
        [sg.T('Image to label'), sg.FileBrowse(key='image_path')],
        [sg.B('Create'), sg.B('Exit')]
    ]

    def process(self):
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
            workspace.show_workspace()


class OpenProjectHandler:
    @staticmethod
    def process():
        path = sg.popup_get_folder('Select Project to Open', default_path=os.getcwd())
        if path is not None:
            os.chdir(path)
            workspace.show_workspace()


class ProjectMenu:
    layout = [[sg.B('Open Existing Project', key='open')],
              [sg.B('Create New Project', key='create')]
              ]

    def process(self):
        window = sg.Window('iTrust', self.layout, finalize=True)
        window_manager = WindowManager(window)
        window_manager.register_handler('open', OpenProjectHandler())
        window_manager.register_handler('create', NewProjectHandler())
        window_manager.run(close=True)


if __name__ == '__main__':
    ProjectMenu().process()
    # CreateProjectHandler().process()
    # OpenProjectHandler().process()
