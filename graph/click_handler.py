import imp
from typing import TYPE_CHECKING, Any

import PySimpleGUI as sg
from pytesseract import pytesseract
from pair_property import global_pair_property, create_new_pair, assign_current_choice
from .dialog import BaseDialog
from .image import CoordinateTransfer
from .label import Label, LabelType
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
        label: Label = self.graph_handler.hovered_label(position)
        if not label or not self.graph_handler.label_to_select_databox:
            return False

        event, values = self.confirm_databox_dialog()
        match event:
            case 'Confirm':
                self.graph_handler.label_to_select_databox.databox = label
                label._type = LabelType.DATABOX
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
    def select_list(title, choices):
        return sg.Tab(title, [[sg.Listbox(choices, s=(40, 20), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, enable_events=True, key=f'list-{title}')]])

    def update_label_dialog(self, label: Label):
        dialog = BaseDialog(label)
        left_layout = dialog.layout()
        left_layout += [
            [sg.B('Update'), sg.Cancel(), sg.B(
                'Delete', button_color='red'), sg.B('Find Similar', key='Similar')]
        ]

        if label.databox:
            button_hint = f'{label.databox.name}. Reselect'
            left_layout += [[sg.B(button_hint, key='Databox',
                                  button_color='blue'), sg.B('Remove Databox')]]
        else:
            left_layout += [[sg.B('Select Databox',
                                  key='Databox', button_color='blue')]]

        left_layout += [[sg.B('Edit Connections', key='Connection')]]
        left_layout += [[sg.B('Try Recognize Text', key='OCR')]]

        pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
        print('Text Recognized:')
        lst = list(filter(bool, pytesseract.image_to_string(
            self.graph_handler.image.crop(label)).split('\n')))
        right_layout = [[sg.TabGroup(
            [[self.select_list('fullname', lst), self.select_list('shortname', lst)]])]]

        print(left_layout)
        left_l = sg.Column(left_layout)
        print(left_l)
        layout = [[left_l, sg.VSep(), sg.Column(right_layout)]]
        # layout = [[sg.Column(left_layout)]] + [[sg.VSep()]] + [[sg.Column(right_layout)]]

        dialog.create('Update', layout)
        return dialog

    def find_similar_labels(self, label):
        coord = CoordinateTransfer(relative_bottom_left=(-1, -1), relative_top_right=(1, 1),
                                   absolute_size=self.graph_handler.image.original_size)
        matches = relative_coord_crop_matching(
            self.graph_handler.image.to_nparray(), label, coord)
        matches = remove_close_rectangles(
            matches, self.graph_handler.labels, min(label.width, label.height))
        for rect in matches:
            similar_label = Label(rect.bottom_left, rect.top_right)
            similar_label.flip = label.flip
            similar_label.category = label.category
            similar_label.rotation = label.rotation

            self.graph_handler.add_label(similar_label)
        self.graph_handler.notify_labels()

    def handle(self, position) -> bool:
        label: Label | None = self.graph_handler.hovered_label(position)
        if not label or self.graph_handler.state is not None:
            return False

        # check whether in create pair mode
        if global_pair_property.current_choice is not None:
            label.parent = global_pair_property.name
            assign_current_choice(label)
            create_new_pair()

        else:
            dialog = self.update_label_dialog(label)
            while True:
                event, values = dialog.read(close=False)
                print(event, values)
                if event in ['Delete']:
                    self.graph_handler.remove_label(label)
                    break
                elif event in ['Update']:
                    label.copy_basic_properties(values)
                    break
                elif event == 'list-shortname':
                    val = values['list-shortname']
                    dialog.window['name'].update(' '.join(val))
                elif event == 'list-fullname':
                    val = values['list-fullname']
                    dialog.window['fullname'].update(' '.join(val))

                elif event == 'name':
                    dialog.window['list-shortname'].update(set_to_index=[])

                elif event == 'fullname':
                    dialog.window['list-fullname'].update(set_to_index=[])

                elif event == 'Databox':
                    self.graph_handler.state = 'select_databox'
                    self.graph_handler.label_to_select_databox = label
                    break
                elif event == 'Remove Databox':
                    label.databox = None
                    break
                elif event == 'Similar':
                    self.find_similar_labels(label)
                    break
                elif event == 'Connection':
                    edit_connection = EditConnectionHandler(
                        self.graph_handler, label)
                    edit_connection.handle()
                elif event == 'OCR':
                    pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
                    print('Text Recognized:')
                    print(pytesseract.image_to_string(
                        self.graph_handler.image.crop(label)))
                elif event in ['Cancel', None]:
                    break
                else:
                    ...
                    # raise AssertionError(event)

            dialog.close()

        self.graph_handler.notify_labels()
        return True


class AddConnectionHandler(ClickHandler):
    def handle(self, position) -> bool:
        label = self.graph_handler.hovered_label(position)
        if not label or self.graph_handler.state != 'add_connection':
            return False

        event, _ = self.confirm_databox_dialog()
        if event == 'Confirm':
            self.graph_handler.context['label_to_add_connection'].add_connection(
                label)
            self.graph_handler.notify_labels()
            self.graph_handler.state = None
        elif event == 'Select Again':
            ...
        elif event in ['Cancel', None]:
            self.graph_handler.state = None

        return True

    @staticmethod
    def confirm_databox_dialog() -> tuple[str, Any]:
        layout = [[sg.B('Confirm'), sg.B('Select Again'), sg.Cancel()]]
        return sg.Window('confirm connection?', layout).read(close=True)


class EditConnectionHandler:
    def __init__(self, graph_handler, label: Label):
        self.graph_handler = graph_handler
        self.label = label
        self.window = None

    def selected_labels(self) -> dict[str, Label]:
        return {f'[{i}]. {conn.name}/{conn.fullname}': conn for i, conn in enumerate(self.label.connections, 1)}

    def unselected_labels(self) -> dict[str, Label]:
        i = 1
        result = {}
        for label in self.graph_handler.labels:
            if label not in self.selected_labels().values():
                result[f'[{i}]. {label.name}/{label.fullname}'] = label
                i += 1

        return result

    def update_ui(self):
        self.update_selected_ui()
        self.update_unselected_ui()

    def update_unselected_ui(self):
        self.window['unselected'].update(
            values=self.unselected_labels().keys())

    def update_selected_ui(self):
        self.window['selected'].update(values=self.selected_labels().keys())

    def layout(self):
        return [
            [sg.T('Selected Connections')],
            [sg.Listbox(values=list(self.selected_labels().keys()), key='selected', s=(30, 5),
                        enable_events=True)],
            [sg.T('Unselected Labels')],
            [sg.Listbox(values=list(self.unselected_labels().keys()), key='unselected', s=(30, 5),
                        enable_events=True)],
            [sg.B('Add', key='add'), sg.B('Remove', key='remove'),
             sg.B('Back', key='back')]
        ]

    def handle(self) -> None:

        self.window = sg.Window(
            'Edit Connections', self.layout(), keep_on_top=True)
        while True:
            event, values = self.window.read(close=False)
            print(event, values)
            if event == 'add':
                hint = values['unselected'][0]
                self.label.add_connection(self.unselected_labels()[hint])
                self.update_ui()
                # self.graph_handler.state = 'add_connection'
                # self.graph_handler.context['label_to_add_connection'] = self.label
                # break

            elif event == 'remove':
                hint = values['selected'][0]
                self.label.remove_connections(self.selected_labels()[hint])
                self.update_ui()

            elif event in ['back', sg.WINDOW_CLOSED]:
                break

        print(self.label.connections)
        self.window.close()


class AddPairHandler(ClickHandler):
    def handle(self, position) -> bool:
        super().handle(position)
        layout = [[sg.T('Pair Name'), sg.I(key='pair_name', default_text=self.graph_handler.pair_parent_name)],
                  [sg.B('Choose Component'), sg.B('Choose Databox'), sg.Cancel()]]
        event, value = sg.Window('Choose Pair', layout=layout).read(close=True)
        self.graph_handler.pair_parent_name = value['pair_name']
        if event == 'Choose Component':
            self.graph_handler.pair_type = LabelType.COMPONENT
        elif event == 'Choose Databox':
            self.graph_handler.pair_type = LabelType.DATABOX
        elif event in ['Cancel']:
            self.graph_handler.pair_type = LabelType.COMPONENT
            self.graph_handler.pair_parent_name = ''
        elif event in [None]:
            pass
        else:
            raise AssertionError()

        print(event, value)
        return False
