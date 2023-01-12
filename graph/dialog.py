import PySimpleGUI as sg
from config import config
from flip_dict import FlipDict

from .label import Label, LabelType


class BaseDialog:
    rotation_options = FlipDict({'None': 0, 'clockwise 90 degrees': 90.0, 'clockwise 180 degrees': 180.0,
                                 'clockwise 270 degrees': 270.0})
    flip_options = FlipDict(
        {'None': 0, 'flip around y axis': 1, 'flip around x axis': 2, 'flip around both x and y axis': 3})

    def __init__(self, label=None):
        self.label = label if label else Label()
        self.window = None

    @property
    def categories(self):
        return config["categories"]

    def layout(self, enable_event=True):
        print('layout', self.label._type)
        if self.label._type == LabelType.COMPONENT:
            default_type_str = 'Component'
        elif self.label._type == LabelType.DATABOX:
            default_type_str = 'Databox'
        else:
            raise ValueError(f'Type of label can\' be {self.label._type}')
        return [
            [sg.T('Name'), sg.I(self.label.name,
                                key='name', enable_events=enable_event)],
            [sg.T('Type'), sg.DD(['Component', 'Databox'], readonly=True,
                                 default_value=default_type_str, key='type')],
            [sg.T('Category'), sg.DD(self.categories,
                                     default_value=self.label.category, key='category')],
            [sg.T('Fullname'), sg.I(self.label.fullname,
                                    key='fullname', enable_events=enable_event)],
            [sg.T('Parent'), sg.I(self.label.parent_component_name,
                                  key='parent_component_name')],
            self.layout_rotation(),
            self.layout_flip(),
            [sg.T('Flip'),
             sg.DD(list(self.flip_options.keys()), default_value=self.flip_options.flip[self.label.flip], readonly=True,
                   key='flip')]
        ]

    def layout_flip(self):
        return [sg.T('Flip'),
         sg.DD(list(self.flip_options.keys()), default_value=self.flip_options.flip[self.label.flip], readonly=True,
               key='flip')]

    def layout_rotation(self):
        return [sg.T('Rotation'),
                sg.DD(list(self.rotation_options.keys()), default_value=self.rotation_options.flip[self.label.rotation],
                      readonly=True, key='rotation')],

    def create(self, title='', layout=None):
        if layout is None:
            layout = self.layout()
        if self.window == None:
            self.window = sg.Window(title, layout, keep_on_top=True)

    def close(self):
        self.window.close()
        self.window = None

    def read(self, title='', layout=None, close=True):
        event, value = self.window.read(close=close)
        if value is None:
            return event, value

        if 'rotation' in value:
            value['rotation'] = self.rotation_options.get(value['rotation'], 0)
        if 'flip' in value:
            value['flip'] = self.flip_options.get(value['flip'], 0)
        if value.get('type'):
            _type = value['type']
            if _type == 'Component':
                value['type'] = 1
            elif _type == 'Databox':
                value['type'] = 2
            else:
                raise ValueError(
                    f'Type of label can either be "Component" or "Databox", but not {_type}')

        print(f'dialog.read: {value}')
        if close:
            self.close()

        return event, value
