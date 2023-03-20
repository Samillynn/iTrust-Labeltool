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
        name_str = self.label.parent + " " + self.label._type.name
        if self.label.parent in ["", None]:
            name_str = ""
        if self.label._type == LabelType.COMPONENT:
            default_type_str = 'Component'
        elif self.label._type == LabelType.DATABOX:
            default_type_str = 'Databox'
        elif self.label._type == LabelType.BUTTON:
            default_type_str = 'Button'
        else:
            raise ValueError(f'Type of label can\' be {self.label._type}')
        return [
            [sg.T('Parent'), sg.I(self.label.parent,
                                key='parent', enable_events=enable_event)],
            [sg.T('Type'), sg.I(self.label.component_type,
                                key='component_type', enable_events=enable_event)],
            [sg.T('Name'), sg.I(name_str,
                                key='name', enable_events=enable_event)],
            [sg.T('Description'), sg.I(self.label.desc,
                                key='desc', enable_events=enable_event)],
            [sg.T('Status'), sg.I(self.label.status,
                                key='status', enable_events=enable_event)],
            [sg.T('State'), sg.I(self.label.state,
                                key='state', enable_events=enable_event)],
            [sg.T('Label Type'), sg.DD(['Component', 'Databox', "Button"], readonly=True,
                                 default_value=default_type_str, key='type')],
            # [sg.T('Category'), sg.DD(self.categories,
            #                          default_value=self.label.category, key='category')],
            # [sg.T('Fullname'), sg.I(self.label.fullname,
            #                         key='fullname', enable_events=enable_event)],
            # [sg.T('Parent'), sg.I(self.label.parent,
            #                       key='parent')],
            self.layout_level(),
            self.layout_rotation(),
            self.layout_flip(),
        ]
        
    def layout_level(self):
        return [sg.T('Level'),
         sg.Checkbox('L', default=self.label.l, key='l'),
          sg.Checkbox('LL', default=self.label.ll, key='ll'),
          sg.Checkbox('H', default=self.label.h, key='h'),]

    def layout_flip(self):
        return [sg.T('Flip'),
         sg.DD(list(self.flip_options.keys()), default_value=self.flip_options.flip[self.label.flip], readonly=True,
               key='flip')]

    def layout_rotation(self):
        return [sg.T('Rotation'),
                sg.DD(list(self.rotation_options.keys()), default_value=self.rotation_options.flip[self.label.rotation],
                      readonly=True, key='rotation')]

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
            elif _type == 'Button':
                value['type'] = 3
            else:
                raise ValueError(
                    f'Type of label can either be "Component", "Databox" or "Button", but not {_type}')

        # print(f'dialog.read: {value}')
        if close:
            self.close()

        return event, value
