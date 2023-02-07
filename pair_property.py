import time
from recordclass import recordclass, asdict
import PySimpleGUI as sg
from base_classes import EventHandler
from config import config

PairProperty = recordclass("PairProperty",
                          fields=["name", "status", "desc", "state", "component_type",
                                       "additional_info", "current_choice", "component", "databox", "button", "choosing", "component_label", "databox_label", "button_label"],
                          defaults=["", "", "", "", "", "", None, None, None, None, False, False, False, False])

global_pair_property = PairProperty()

class NewPairEH(EventHandler):
    def __init__(self, graph_handler=None):
        self.graph_handler = graph_handler
    # def cancel_activity(self, label):
        
        
    def handle(self):
        global_pair_property.choosing = False
        self.graph_handler.image.remove_shadow()
        self.graph_handler.notify_image()
        def get_button_color(button_name):
            if button_name == "Component":
                label = global_pair_property.component
            elif button_name == "Databox":
                label = global_pair_property.databox
            elif button_name == "Button":
                label = global_pair_property.button
            else:
                raise AssertionError

            return "blue" if label is not None else "grey"

        layout = [
            [sg.T("Name"), sg.I(key="name", default_text=global_pair_property.name)],
            [sg.T("Type"), sg.I(key="component_type", default_text=global_pair_property.component_type)],
            [sg.T("Description"), sg.I(key="desc", default_text=global_pair_property.desc)],
            [sg.T("Status"), sg.I(key="status", default_text=global_pair_property.status)],
            [sg.T("State"), sg.I(key="state", default_text=global_pair_property.state)],
            # [sg.T('Category'), sg.DD(config["categories"], key='category', default_value=global_pair_property.category)],
            # [sg.T("Additional info"), sg.I(key="additional_info", default_text=global_pair_property.additional_info)],
            [sg.B("Component", button_color=get_button_color("Component")), sg.B("Databox", button_color=get_button_color("Databox")), sg.B("Button", button_color=get_button_color("Button")), sg.Cancel(), sg.B("Done")]
        ]
        event, values = sg.Window("Create New", layout).read(close=True)
        
        component = global_pair_property.component
        databox = global_pair_property.databox
        button = global_pair_property.button

        if event in ['Component', 'Databox', 'Button', 'Cancel', None]:
            global_pair_property.name = values["name"]
            global_pair_property.component_type = values["component_type"]
            global_pair_property.status = values["status"]
            global_pair_property.state = values["state"]
            global_pair_property.desc = values["desc"]

            if event == 'Component':
                if component is not None and not global_pair_property.component_label:
                    self.graph_handler.remove_label(component)
                global_pair_property.current_choice = 'Component'
                global_pair_property.choosing = True
                self.graph_handler.image.add_shadow()
                self.graph_handler.notify_image()
            elif event == 'Databox':
                if databox is not None and not global_pair_property.databox_label:
                    self.graph_handler.remove_label(databox)
                global_pair_property.current_choice = 'Databox'
                global_pair_property.choosing = True
                self.graph_handler.image.add_shadow()
                self.graph_handler.notify_image()
            elif event == 'Button':
                if button is not None and not global_pair_property.button_label:
                    self.graph_handler.remove_label(button)
                global_pair_property.current_choice = 'Button'
                global_pair_property.choosing = True
                self.graph_handler.image.add_shadow()
                self.graph_handler.notify_image()
            elif event in ['Cancel', None]:
                if component is not None and not global_pair_property.component_label:
                    self.graph_handler.remove_label(component)
                if databox is not None and not global_pair_property.databox_label:
                    self.graph_handler.remove_label(databox)
                if button is not None and not global_pair_property.button_label:
                    self.graph_handler.remove_label(button)
                self.graph_handler.notify_labels()
                global_pair_property.name = ""
                global_pair_property.component_type = ""
                global_pair_property.status = ""
                global_pair_property.state = ""
                global_pair_property.desc = ""
                global_pair_property.current_choice = None
                global_pair_property.component = None
                global_pair_property.databox = None
                global_pair_property.button = None
                global_pair_property.component_label = False
                global_pair_property.databox_label = False
                global_pair_property.button_label = False
                
        elif event == 'Done':
            global_pair_property.name = values["name"]
            global_pair_property.component_type = values["component_type"]
            global_pair_property.status = values["status"]
            global_pair_property.state = values["state"]
            global_pair_property.desc = values["desc"]
            label_dict = asdict(global_pair_property)
            label_dict["parent"] = label_dict["name"]
            if component is not None:
                label_type = component._type
                component.copy_basic_properties(label_dict)
                component._type = label_type
            if databox is not None:
                label_type = databox._type
                databox.copy_basic_properties(label_dict)
                databox._type = label_type
                print(databox._type)
            if button is not None:                
                label_type = button._type
                button.copy_basic_properties(label_dict)
                button._type = label_type

            self.graph_handler.notify_labels()
            global_pair_property.name = ""
            global_pair_property.component_type = ""
            global_pair_property.status = ""
            global_pair_property.state = ""
            global_pair_property.desc = ""
            # global_pair_property.additional_info = ""
            global_pair_property.current_choice = None
            global_pair_property.component = None
            global_pair_property.databox = None
            global_pair_property.button = None
            global_pair_property.component = None
            global_pair_property.databox = None
            global_pair_property.button = None
            global_pair_property.component_label = False
            global_pair_property.databox_label = False
            global_pair_property.button_label = False
            
        else:
            raise AssertionError


def assign_current_choice(label):
    if global_pair_property.current_choice == 'Component':
        global_pair_property.component = label
    elif global_pair_property.current_choice == 'Databox':
        global_pair_property.databox = label
    elif global_pair_property.current_choice == 'Button':
        global_pair_property.button = label
    else:
        raise AssertionError


if __name__ == "__main__":
    print(global_pair_property)
