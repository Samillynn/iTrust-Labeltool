from typing import Collection

import PySimpleGUI as sg

from v3.event import Event
from v3.graph_handler import GraphController, GraphView
from v3.handler import HandlerChain
from v3.key_handler import KeyHandler
from v3.label import Label
from v3.session_storage import SessionStorage


def show_workspace():
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
            expand_x=True,
            expand_y=True)],
        [sg.Text(key='info', size=(60, 1)), sg.I(visible=False, enable_events=True, key='export-filename'),
         sg.SaveAs('Export', key='-EXPORT-', file_types=(('JSON file', '*.json'),),
                   target='export-filename'),
         sg.B('New', key='-NEW-'), sg.B('Open', key='-OPEN-')]
    ]

    window = sg.Window("Workplace", layout, finalize=True, return_keyboard_events=True, resizable=True)
    graph = window['-GRAPH-']

    # storage = JsonStorage('session.json')
    graph_controller = GraphController(MockStorage())
    graph_view = GraphView()
    graph_view.image = graph_controller.image
    graph_view.draw(graph, image=True)

    window_handler = HandlerChain()
    window_handler.add_handler(KeyHandler('-GRAPH-', graph_controller))

    while True:
        event, values = window.read()
        e = Event(event, values, graph_controller)
        window_handler.handle(e)
        graph_view.labels = graph_controller.labels
        graph_view.draw(graph, image=False)
        if e.name.endswith('+UP'):
            print(graph_controller.labels)


if __name__ == '__main__':
    class MockStorage(SessionStorage):

        @property
        def image_path(self) -> str:
            return 'screen_shot.jpg'

        @property
        def labels(self) -> Collection[Label]:
            return []


    show_workspace()
