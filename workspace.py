import logging
import os

import PySimpleGUI as sg

from graph_handler import GraphHandler
from project_handlers import NewProjectHandler, OpenProjectHandler
from window_manager import WindowManager

logging.basicConfig(level=logging.INFO)


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

    window_manager.register_handler('-NEW-', NewProjectHandler())
    window_manager.register_handler('-OPEN-', OpenProjectHandler())
    window_manager.run()


if __name__ == '__main__':
    show_workspace('.')
