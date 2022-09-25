from typing import TYPE_CHECKING

import PySimpleGUI as sg

from .dialog import BaseDialog
from .image import CoordinateTransfer
from .label import Label
from .template_matching2 import relative_coord_crop_matching, remove_close_rectangles

if TYPE_CHECKING:
    from .graph_handler import GraphHandler


class ClickHandler:
    def __init__(self, graph_handler):
        self.graph_handler: GraphHandler = graph_handler

    def handle(self, position) -> bool:
        return False


class SelectDataboxHandler(ClickHandler):
    def handle(self, position) -> bool:
        label = self.graph_handler.hovered_label(position)
        if not label or not self.graph_handler.label_to_select_databox:
            return False

        event, values = self.confirm_databox_dialog()
        match event:
            case 'Confirm':
                self.graph_handler.label_to_select_databox.databox = label
                self.graph_handler.notify_labels()
                self.graph_handler.state = None
            case 'Select Again':
                ...
            case 'Cancel' | None:
                self.graph_handler.label_to_select_databox = None
            case _:
                raise AssertionError('Unsupported Event')

    @staticmethod
    def confirm_databox_dialog():
        layout = [[sg.B('Confirm'), sg.B('Select Again'), sg.Cancel()]]
        return sg.Window('confirm Databox?', layout).read(close=True)


class UpdateLabelHandler(ClickHandler):

    @staticmethod
    def update_label_dialog(label: Label):
        dialog = BaseDialog(label)
        layout = dialog.layout()
        layout += [
            [sg.B('Update'), sg.Cancel(), sg.B('Delete', button_color='red'), sg.B('Find Similar', key='Similar')]
        ]

        if label.databox:
            button_hint = f'{label.databox.name}. Reselect'
            layout += [[sg.B(button_hint, key='Databox', button_color='blue'), sg.B('Remove Databox')]]
        else:
            layout += [[sg.B('Select Databox', key='Databox', button_color='blue')]]

        layout += [[sg.B('Edit Connections', key='Connection')]]

        return dialog.read('Update Label', layout)

    def find_similar_labels(self, label):
        coord = CoordinateTransfer(relative_bottom_left=(-1, -1), relative_top_right=(1, 1),
                                   absolute_size=self.graph_handler.image.size)
        matches = relative_coord_crop_matching(self.graph_handler.image.to_nparray(), label, coord)
        matches = remove_close_rectangles(matches, self.graph_handler.labels, min(label.width, label.height))
        for rect in matches:
            self.graph_handler.add_label(Label(rect.bottom_left, rect.top_right))
        self.graph_handler.notify_labels()

    def handle(self, position) -> bool:
        label: Label | None = self.graph_handler.hovered_label(position)
        if not label or self.graph_handler.state is not None:
            return False

        event, values = self.update_label_dialog(label)
        if event in ['Delete']:
            self.graph_handler.remove_label(label)
        elif event in ['Update']:
            print(values)
            label.copy_basic_properties(values)
        elif event == 'Databox':
            self.graph_handler.state = 'select_databox'
            self.graph_handler.label_to_select_databox = label
        elif event == 'Remove Databox':
            label.databox = None
        elif event == 'Similar':
            self.find_similar_labels(label)
        elif event == 'Connection':
            edit_connection = EditConnectionHandler(self.graph_handler, label)
            edit_connection.handle()
        elif event in ['Cancel', None]:
            ...
        else:
            raise AssertionError(event)

        self.graph_handler.notify_labels()
        return True


class AddConnectionHandler(ClickHandler):
    def handle(self, position) -> bool:
        label = self.graph_handler.hovered_label(position)
        if not label or self.graph_handler.state != 'add_connection':
            return False

        event, _ = self.confirm_databox_dialog()
        if event == 'Confirm':
            self.graph_handler.context['label_to_add_connection'].add_connection(label)
            self.graph_handler.state = None
        elif event == 'Select Again':
            ...
        elif event in ['Cancel', None]:
            self.graph_handler.state = None

        return True

    @staticmethod
    def confirm_databox_dialog():
        layout = [[sg.B('Confirm'), sg.B('Select Again'), sg.Cancel()]]
        return sg.Window('confirm connection?', layout).read(close=True)


class EditConnectionHandler:
    def __init__(self, graph_handler, label: Label):
        self.graph_handler = graph_handler
        self.label = label

    def hints(self):
        return {f'{conn.name}/{conn.fullname}': conn for conn in self.label.connections}

    def layout(self):
        return [
            [sg.Listbox(values=list(self.hints().keys()), key='select', s=(30, 5), enable_events=True)],
            [sg.B('Add', key='add'), sg.B('Remove', key='remove'), sg.B('Back', key='back')]
        ]

    def handle(self) -> None:
        window = sg.Window('Edit Connections', self.layout())
        while True:
            event, values = window.read(close=False)
            print(event, values)
            if event == 'add':
                self.graph_handler.state = 'add_connection'
                self.graph_handler.context['label_to_add_connection'] = self.label
                break

            elif event == 'remove':
                print(values)
                hint = values['select'][0]
                self.label.remove_connections(self.hints()[hint])
                window['select'].update(values=self.hints().keys())

            elif event in ['back', sg.WINDOW_CLOSED]:
                break

        window.close()
