from typing import TYPE_CHECKING

from utils import sg
from .dialog import base_dialog_layout, BaseDialog
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
                self.graph_handler.label_to_select_databox = None
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
        if not label or self.graph_handler.label_to_select_databox:
            return False

        event, values = self.update_label_dialog(label)
        if event in ['Delete']:
            self.graph_handler.remove_label(label)
        elif event in ['Update']:
            label.name = values['name']
            label.category = values['type']
            label.text = values['text']
            label.rotation = values['rotation']
            label.flip = values['flip']
        elif event == 'Databox':
            self.graph_handler.label_to_select_databox = label
        elif event == 'Remove Databox':
            label.databox = None
        elif event == 'Similar':
            self.find_similar_labels(label)
        elif event in ['Cancel', None]:
            ...
        else:
            raise AssertionError(event)

        self.graph_handler.notify_labels()
        return True
