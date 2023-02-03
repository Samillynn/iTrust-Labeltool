import imp
import json
import os
import shutil
from pathlib import Path

import globl
import modifier_key
from base_classes import EventHandler
from config import config
from graph.graph_manager import GraphManager
from graph.label import LabelListSerializer, LabelType, Rectangle
from utils import sg, current_milli_time
from window_manager import WindowManager
from graph.label import LabelListSerializer, Label
from pair_property import global_pair_property, NewPairEH


class NewProjectEH(EventHandler):
    layout = [
        [sg.T('Location:'), sg.FolderBrowse(
            key='location', initial_folder=os.getcwd())],
        [sg.T('Project Name:'), sg.I(key='project_name')],
        [sg.T('Image to label'), sg.FileBrowse(key='image_path')],
        [sg.B('Create'), sg.B('Exit')]
    ]

    def handle(self):
        event, values = sg.Window(
            'Create New Project', self.layout).read(close=True)
        if event in ['Create']:
            project_path = Path(values['location'], values['project_name'])
            # TODO: delete exist_ok
            project_path.mkdir(exist_ok=True)
            os.chdir(project_path)

            old_image_path = Path(values['image_path'])
            new_image_path = f'{current_milli_time()}-{old_image_path.name}'
            shutil.copyfile(old_image_path, new_image_path)
            session = {
                "image_path": new_image_path,
                "labels": []
            }
            json.dump(session, open('session.json', 'w+'))
            show_workspace()


class OpenProjectEH(EventHandler):
    def handle(self):
        path = sg.popup_get_folder(
            'Select Project to Open', default_path=os.getcwd())
        if path is not None:
            os.chdir(path)
            show_workspace()


class ProjectMenuEH(EventHandler):
    layout = [[sg.B('Open Existing Project', key='open')],
              [sg.B('Create New Project', key='create')]
              ]

    def handle(self):
        window = sg.Window('iTrust', self.layout, finalize=True)
        window_manager = WindowManager(window)
        window_manager.register_handler('open', OpenProjectEH())
        window_manager.register_handler('create', NewProjectEH())
        window_manager.run(close=True)


# def export_eh(event, file_path):
#     def convert_label(label_dict):
#         top_left = label_dict.pop('top_left')
#         bottom_right = label_dict.pop('bottom_right')
#         rect = Rectangle(top_left, bottom_right)
#         label_dict['coordinate'] = rect.center
#         label_dict['width'] = rect.height
#         label_dict['length'] = rect.width

#         if label_dict.get('databox'):
#             label_dict['databox'] = Rectangle(label_dict['databox']['top_left'],
#                                               label_dict['databox']['bottom_right']).center
#             print(label_dict)
#         else:
#             label_dict['databox'] = []

#     labels = json.load(open('session.json', 'r'))['labels']
#     for label in labels:
#         convert_label(label)
#     json.dump(labels, open(file_path, 'w+'), indent=2)

def convert_json(result):
    cleaned_result = []
    for name,values in result.items():
        component_value = values.get("component",None)
        databox_value = values.get("databox",None)
        button_value = values.get("button",None)
        
        status = ""
        state = ""
        desc = ""
        
        # check whether status and desc are assigned
        flag = False
            
        if component_value is not None:
            status = component_value.get("status","")
            state = component_value.get("state","")
            desc = component_value.get("desc","")
            component_value = {
                "flip":component_value.get("flip"),
                "rotation":component_value.get("rotation"),
                "coordinate":component_value.get("coordinate")
            }
            
        if databox_value is not None:
            if not flag:
                status = databox_value.get("status","")
                state = databox_value.get("state","")
                desc = databox_value.get("desc","")
                flag = True   
            databox_value = {
                "coordinate":databox_value.get("coordinate")
            } 
            
        if button_value is not None:
            if not flag:
                status = button_value.get("status","")
                state = button_value.get("state","")
                desc = button_value.get("desc","")
            button_value = {
                "coordinate":button_value.get("coordinate")
            }
            
        new_obj = {
            "name":name,
            "type":"".join([c for c in name if c.isalpha()]),
            "description":desc,
            "status":status,
            "state":state,
        }
        
        if component_value is not None:
            new_obj['component'] = component_value
        else:
            new_obj['component'] = {}
        if databox_value is not None:
            new_obj['databox'] = databox_value
        else:
            new_obj['databox'] = {}
        if button_value is not None:
            new_obj['button'] = button_value
        else:
            new_obj['button'] = {}
            
        cleaned_result.append(new_obj)
            
    return cleaned_result

def export_eh(event, file_path):
    def to_export_label_dict(label: Label, result_dict):
        valid = True
        result = label.basic_properties
        result['coordinate'] = label.center
        # if label.databox is not None:
        #     result['databox'] = list(label.databox.center)
        # else:
        #     result['databox'] = []

        # parent_name = result['parent_component_name']
        # print(f'calling to_eld, pn={parent_name}')
        # if parent_name not in result_dict:
        #     result_dict[parent_name] = [result]
        #     result_dict[parent_name] = {}
        if result['type'] == 1:
            result_type = 'component'
        elif result['type'] == 2:
            result_type = 'databox'
        elif result['type'] == 3:
            result_type = 'button'
        else:
            raise AssertionError()
        
        result_name = result["parent"]

        if result_name not in result_dict:
            result_dict[result_name] = {}
                        
        required_properties = {
            "name":result["name"],
            "desc":result["desc"],
            "status":result["status"],
            "state":result["state"],
            "type":result["type"],
            "flip":result["flip"],
            "rotation":result["rotation"],
            "coordinate":result["coordinate"]    
        }
        if result_type not in result_dict[result_name]:
            result_dict[result_name][result_type] = required_properties
        else:
            prev_obj = result_dict[result_name][result_type]
            sg.popup(
                f'{prev_obj["name"]} has the same parent with {result["name"]}', title='Repeated Parent Name')
            valid = False

        return valid

    label_dicts = json.load(open('session.json', 'r'))['labels']
    labels = LabelListSerializer().deserialize(label_dicts)
    # export_label_dicts = [
    #     to_export_label_dict(label)  for label in labels if label._type == LabelType.COMPONENT
    # ]
    result = {}
    for label in labels:
        if not to_export_label_dict(label, result):
            return
    cleaned_result = convert_json(result)
    json.dump(cleaned_result, open(file_path, 'w+'), indent=2)


class Workspace:
    def __init__(self, root_path='.'):
        self.window = sg.Window(layout=self.layout(
        ), finalize=True, return_keyboard_events=True, resizable=True)
        self.root_path = root_path
        self.bind_keys()

    def bind_keys(self):
        self.window.bind('<Key-Control_L>', 'KeyDown-Control')
        self.window.bind('<Key-Control_R>', 'KeyDown-Control')

    @staticmethod
    def layout():
        return [
            [sg.Graph(
                canvas_size=(0, 0),
                graph_bottom_left=(-1, -1),
                graph_top_right=(1, 1),
                key="-GRAPH-",
                change_submits=True,  # mouse click events
                background_color='lightblue',
                drag_submits=True,
                motion_events=True,
                float_values=True,
                expand_x=False,
                expand_y=False)],
            [sg.Text(key='info', size=(60, 1)), sg.I(visible=False, enable_events=True, key='export-filename'),
             sg.SaveAs('Export', key='-EXPORT-', file_types=(('JSON file', '*.json'),),
                       target='export-filename'),
             sg.B('New', key='-NEW-'), sg.B('Open', key='-OPEN-'), sg.B('Show/Hide connections', key='connections')],
        ]


def toggle_connections(event, values):
    print(f'connection enable={globl.connection_view.enabled}.')
    globl.connection_view.enabled = not globl.connection_view.enabled


# Show workspace
def show_workspace(project_path=None):
    layout = [
        [sg.Graph(
            canvas_size=(0, 0),
            graph_bottom_left=(-1, -1),
            graph_top_right=(1, 1),
            key="-GRAPH-",
            change_submits=True,  # mouse click events
            background_color='lightblue',
            drag_submits=True,
            motion_events=True,
            float_values=True,
            expand_x=False,
            expand_y=False)],
        [sg.Text(key='info', size=(0, 0)), sg.I(visible=False, enable_events=True, key='export-filename'),
         sg.Text(key='info', size=(0, 0)), sg.I(visible=False,
                                                enable_events=True, key='export-conn-filename'),

         sg.SaveAs('Export', key='-EXPORT-', file_types=(('JSON file', '*.json'),),
                   target='export-filename'),

         sg.SaveAs('Export Connections', key='-EXPORT-CONN-', file_types=(('JSON file', '*.json'),),
                   target='export-conn-filename'),

         sg.B('New', key='-NEW-'), sg.B('Open',
                                        key='-OPEN-'), sg.B('Show/Hide Connections', key='-CONN-'),

         sg.B('Create New', key='-CREATE-'),
         sg.B('Return', key='-RETURN-', visible=False),
         ]
    ]

    if project_path is not None:
        os.chdir(project_path)
    window = sg.Window("Workplace", layout, finalize=True,
                       return_keyboard_events=True, resizable=True)
    window.bind('<Key-Control_L>', 'KeyDown-Control')
    window.bind('<Key-Control_R>', 'KeyDown-Control')

    window_manager = WindowManager(window)

    window_manager.register_handler('', modifier_key.listen)
    graph_manager = GraphManager(window['-GRAPH-'])
    window_manager.add_handler(graph_manager)

    def export_conn_eh(event, file_path):
        print("calling export_conn_eh")
        result = {}
        for label in graph_manager.handler.labels:
            key_format = config["export"]["connection"]["key_format"]
            val_format = config["export"]["connection"]["val_format"]
            key = key_format.format(**label.basic_properties)
            val = [val_format.format(**conn.basic_properties)
                   for conn in label.connections]
            result[key] = val
        json.dump(result, open(file_path, 'w+'), indent=2)
    
    def return_to_create_new(event):
        if global_pair_property.current_choice is not None:
            graph_manager.handler.image.remove_shadow()
            graph_manager.handler.notify_image()
            handler = NewPairEH(graph_manager.handler)
            handler.handle()

    window_manager.register_handler('-NEW-', NewProjectEH())
    window_manager.register_handler('-OPEN-', OpenProjectEH())
    window_manager.register_handler('export-filename', export_eh)
    window_manager.register_handler('-CONN-', toggle_connections)
    window_manager.register_handler('export-conn-filename', export_conn_eh)
    window_manager.register_handler('-CREATE-', NewPairEH(graph_manager.handler))
    window_manager.register_handler('-RETURN-', return_to_create_new)
    window_manager.run()


if __name__ == '__main__':
    show_workspace('')
