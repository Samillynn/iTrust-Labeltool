import PySimpleGUI as sg
from flip_dict import FlipDict

from .label import Label


class BaseDialog:
    rotation_options = FlipDict({'None': 0, 'clockwise 90 degrees': 90.0, 'clockwise 180 degrees': 180.0,
                                 'clockwise 270 degrees': 270.0})
    flip_options = FlipDict(
        {'None': 0, 'flip around y axis': 1, 'flip around x axis': 2, 'flip around both x and y axis': 3})

    categories = ['big tank', 'small tank', 'pump', 'dosing pump', 'uv dechlorinator', 'filter', 'other types']

    def __init__(self, label=None):
        self.label = label if label else Label()

    def layout(self):
        return [
            [sg.T('Name'), sg.I(self.label.name, key='name')],
            [sg.T('Category'), sg.DD(self.categories, default_value=self.label.category, key='category')],
            [sg.T('Fullname'), sg.I(self.label.fullname, key='fullname')],
            [sg.T('Parent'), sg.I(self.label.parent, key='parent')],
            [sg.T('Rotation'),
             sg.DD(list(self.rotation_options.keys()), default_value=self.rotation_options.flip[self.label.rotation],
                   readonly=True, key='rotation')],
            [sg.T('Flip'),
             sg.DD(list(self.flip_options.keys()), default_value=self.flip_options.flip[self.label.flip], readonly=True,
                   key='flip')]
        ]

    def read(self, title='', layout=None):
        if layout is None:
            layout = self.layout()

        event, value = sg.Window(title, layout).read(close=True)
        if 'rotation' in value:
            value['rotation'] = self.rotation_options.get(value['rotation'], 0)
        if 'flip' in value:
            value['flip'] = self.flip_options.get(value['flip'], 0)

        return event, value


def base_dialog_layout(label=None):
    dialog_options = {
        'category': ['big tank', 'small tank', 'pump', 'dosing pump', 'uv dechlorinator', 'filter', 'other types'],
        'rotation': [None, 'clockwise 90 degrees', 'clockwise 180 degrees', 'clockwise 270 degrees'],
        'flip': [None, 'flip around y axis', 'flip around x axis', 'flip around both x and y axis']
    }

    if label is None:
        label = Label()
    return [
        [sg.T('Name'), sg.I(label.name, key='name')],
        [sg.T('Type'), sg.DD(dialog_options['type'], default_value=label.category, key='type')],
        [sg.T('Text'), sg.I(label.text, key='text')],
        [sg.T('Rotation'), sg.DD(dialog_options['rotation'], default_value=label.rotation, key='rotation')],
        [sg.T('Flip'), sg.DD(dialog_options['flip'], default_value=label.flip, key='flip')]
    ]
