from recordclass import recordclass
import PySimpleGUI as sg
from base_classes import EventHandler
from config import config

PairProperty = recordclass("PairProperty",
                          fields=["name", "status", "desc",
                                       "additional_info", "current_choice", "component", "databox", "choosing"],
                          defaults=["", "", "", "", None, None, None, False])

global_pair_property = PairProperty()

class NewPairEH(EventHandler):
    def __init__(self, graph_handler=None):
        self.graph_handler = graph_handler
    def handle(self):
        global_pair_property.choosing = False
        print(global_pair_property.choosing)
        self.graph_handler.image.remove_shadow()
        self.graph_handler.notify_image()
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
            [sg.T("Status"), sg.I(key="status", default_text=global_pair_property.status)],
            [sg.T("Description"), sg.I(key="desc", default_text=global_pair_property.desc)],
            # [sg.T('Category'), sg.DD(config["categories"], key='category', default_value=global_pair_property.category)],
            # [sg.T("Additional info"), sg.I(key="additional_info", default_text=global_pair_property.additional_info)],
            [sg.B("Component", button_color=get_button_color("Component")), sg.B("Databox", button_color=get_button_color("Databox")), sg.Cancel(), sg.B("Done")]
        ]
        event, values = sg.Window("Create New", layout).read(close=True)

        if event in ['Component', 'Databox', 'Cancel', None]:
            global_pair_property.name = values["name"]
            global_pair_property.status = values["status"]
            global_pair_property.desc = values["desc"]

            if event == 'Component':
                global_pair_property.current_choice = 'Component'
                global_pair_property.choosing = True
                self.graph_handler.image.add_shadow()
                self.graph_handler.notify_image()
            elif event == 'Databox':
                global_pair_property.current_choice = 'Databox'
                global_pair_property.choosing = True
                self.graph_handler.image.add_shadow()
                self.graph_handler.notify_image()
            elif event in ['Cancel', None]:
                global_pair_property.current_choice = None
                global_pair_property.component = None
                global_pair_property.databox = None
        elif event == 'Done':
            global_pair_property.name = ""
            global_pair_property.status = ""
            global_pair_property.desc = ""
            # global_pair_property.additional_info = ""
            global_pair_property.current_choice = None
            global_pair_property.component = None
            global_pair_property.databox = None
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
