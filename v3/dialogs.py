import PySimpleGUI as sg

from event import Event
from v3.label import Label

DIALOG_OPTIONS = {
    'type': ['Big Tank', 'Small Tank', 'Pump', 'Dosing Pump', 'UV Dechlorinator', 'Filter', 'Other types']
}


def update_label_dialog(label):
    layout = base_dialog_layout(label)
    layout += [[sg.B('Update'), sg.Cancel(), sg.B('Delete', button_color='red')]]
    return Event(*sg.Window('Update label', layout).read(close=True))


def new_label_dialog():
    layout = base_dialog_layout()
    layout += [[sg.Submit(), sg.Exit()]]
    return Event(*sg.Window('Create new label', layout).read(close=True))


def base_dialog_layout(label=None):
    if label is None:
        label = Label()
    return [
        [sg.T('Name'), sg.I(label.name, key='name')],
        [sg.T('Category'), sg.DD(DIALOG_OPTIONS['type'], default_value=label.category, key='category')],
        [sg.T('Text'), sg.I(label.text, key='text')],
    ]
