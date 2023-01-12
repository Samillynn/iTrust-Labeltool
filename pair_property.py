from recordclass import recordclass
import PySimpleGUI as sg
from config import config

PairProperty = recordclass("PairProperty",
                          fields=["name", "category",
                                       "additional_info", "current_choice", "component", "databox"],
                          defaults=["", "", "", None, None, None])

global_pair_property = PairProperty()


def create_new_pair():
    def get_button_color(button_name):
        if button_name == "Component":
            label = global_pair_property.component
        elif button_name == "Databox":
            label = global_pair_property.databox
        else:
            raise AssertionError

        return "blue" if label is not None else "grey"

    layout = [
        [sg.T("Name"), sg.I(key="name", default_text=global_pair_property.name)],
        [sg.T('Category'), sg.DD(config["categories"], key='category', default_value=global_pair_property.category)],
        [sg.T("Additional info"), sg.I(key="additional_info", default_text=global_pair_property.additional_info)],
        [sg.B("Component", button_color=get_button_color("Component")), sg.B("Databox", button_color=get_button_color("Databox")), sg.Cancel(), sg.B("Done")]
    ]

    event, values = sg.Window("Create New", layout).read(close=True)

    if event in ['Component', 'Databox', 'Cancel']:
        global_pair_property.name = values["name"]
        global_pair_property.category = values["category"]
        global_pair_property.additional_info = values["additional_info"]

        if event == 'Component':
            global_pair_property.current_choice = 'Component'
        elif event == 'Databox':
            global_pair_property.current_choice = 'Databox'
        elif event in ['Cancel', None]:
            global_pair_property.current_choice = None
    elif event == 'Done':
        global_pair_property.name = ""
        global_pair_property.category = ""
        global_pair_property.additional_info = ""
        global_pair_property.current_choice = None
    else:
        raise AssertionError


def assign_current_choice(label):
    if global_pair_property.current_choice == 'Component':
        global_pair_property.component = label
    elif global_pair_property.current_choice == 'Databox':
        global_pair_property.databox = label
    else:
        raise AssertionError


if __name__ == "__main__":
    print(global_pair_property)
