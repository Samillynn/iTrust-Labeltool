from .label import Label
from utils import sg


def base_dialog_layout(label=None):
    dialog_options = {
        'type': ['Big Tank', 'Small Tank', 'Pump', 'Dosing Pump', 'UV Dechlorinator', 'Filter', 'Other types']
    }
    if label is None:
        label = Label()
    return [
        [sg.T('Name'), sg.I(label.name, key='name')],
        [sg.T('Type'), sg.DD(dialog_options['type'], default_value=label.category, key='type')],
        [sg.T('Text'), sg.I(label.text, key='text')],
    ]
