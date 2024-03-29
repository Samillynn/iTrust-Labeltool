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
from utils import sg, current_milli_time, align_center
from window_manager import WindowManager
from graph.label import LabelListSerializer, Label
from pair_property import global_pair_property, NewPairEH


def match_type(component_type):
    type_list = config["type"]
    cleaned_type = "".join(l for l in component_type if l.isalpha())
    for i in range(len(cleaned_type)):
        sub_cleaned_type = cleaned_type[:len(cleaned_type)-i]
        if sub_cleaned_type in type_list:
            return sub_cleaned_type
    return "other"

class NewProjectEH(EventHandler):
    def handle(self):
        layout = [
        [sg.T('Location:'), sg.FolderBrowse(
            key='location', initial_folder=os.getcwd())],
        [sg.T('Project Name:'), sg.I(key='project_name')],
        [sg.T('Image to label'), sg.FileBrowse(key='image_path')],
        [sg.B('Create'), sg.B('Exit')]
    ]
        event, values = sg.Window(
            'Create New Project', layout).read(close=True)
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
        if path is not None and path != "":
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


def convert_json(result, headers):
    cleaned_result = []
    x_set_component = []
    y_set_component = []
    x_set_databox = []
    y_set_databox = []
    x_set_button = []
    y_set_button = []
    
    for name,values in result.items():
        component_value = values.get("component",None)
        databox_value = values.get("databox",None)
        button_value = values.get("button",None)

        component_type = ""        
        status = ""
        state = ""
        desc = ""
        
        # check whether status and desc are assigned
        flag = False
            
        if component_value is not None:
            status = component_value.get("status","")
            state = component_value.get("state","")
            component_type = component_value.get("component_type","")
            desc = component_value.get("desc","")
            component_value = {
                "level":component_value.get("level"),
                "flip":component_value.get("flip"),
                "rotation":component_value.get("rotation"),
                "coordinate":align_center(component_value.get("coordinate"), x_set_component, y_set_component),
                "width":component_value.get("width"),
                "height":component_value.get("height"),
            }
            
        if databox_value is not None:
            if not flag:
                status = databox_value.get("status","")
                state = databox_value.get("state","")
                component_type = databox_value.get("component_type","")
                desc = databox_value.get("desc","")
                flag = True   
            databox_value = {
                "coordinate": align_center(databox_value.get("coordinate"), x_set_databox, y_set_databox),
                "width":databox_value.get("width"),
                "height":databox_value.get("height"),                
            } 
            
        if button_value is not None:
            if not flag:
                status = button_value.get("status","")
                state = button_value.get("state","")
                component_type = button_value.get("component_type","")
                desc = button_value.get("desc","")
            button_value = {
                "coordinate": align_center(button_value.get("coordinate"), x_set_button, y_set_button),
                "width":button_value.get("width"),
                "height":button_value.get("height"), 
            }
        
        matched_type = match_type(name)
        new_obj = {
            "name":name,
            "type":matched_type if component_type == "" else component_type,
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
        
    # ajust size
    def ajust_size(cleaned_result):
        dic = {}
        num_count = {}
        threshold = 0.2
        for cleaned_r in cleaned_result:
            if len(cleaned_r["component"]) != 0:
                component = cleaned_r["component"]
                w_r = component["width"]
                h_r = component["height"]
                _type = cleaned_r["type"]
                if _type not in dic:
                    dic[_type] = (w_r, h_r, 1)
                    component["size_type"] = _type
                    num_count[_type] = 1
                else:
                    # is in and width height about the same
                    flag = True
                    for all_type in dic:
                        if all_type.startswith(_type):
                            w = dic[all_type][0]
                            h = dic[all_type][1]
                            times = dic[_type][2]
                            if (abs(w-w_r)/w<threshold and abs(h-h_r)/h<threshold):
                                # update the size dict
                                new_tuple = ((w*times+w_r)/(times+1), (h*times+h_r)/(times+1), times+1)
                                dic[all_type] = new_tuple
                                component["size_type"] = all_type
                                flag = False
                                break
                            # width height not the same: create a new string e.g. LIT_1
                    if flag:
                        num_count[_type] += 1
                        new_size_type = _type + str(num_count[_type])
                        new_tuple = (w_r, h_r, 1)
                        dic[new_size_type] = new_tuple
                        component["size_type"] = new_size_type

        for cleaned_r in cleaned_result:
            if len(cleaned_r["component"]) != 0:
                component = cleaned_r["component"]
                _type = component["size_type"]
                component["width"] = dic[_type][0]
                component["height"] = dic[_type][1]
        
        print(dic)        
        
    ajust_size(cleaned_result)
        
    # process header
    def auto_align(value, template, threshold=0.05, isCoord=False): 
        for t in template:
            if not isCoord:
                if abs(value-t)/t<threshold:
                    return t
            else:
                if abs(value-t)<0.03:
                    return t
        template.append(value)
        return value
    
    template_witdh = []
    template_height = []
    template_center_x = []
    template_center_y = []
    for header in headers:
        coord = header["coordinate"]
        w = header["width"]
        h = header["height"]
        x = coord[0]
        y = coord[1]
        w = auto_align(w, template_witdh, threshold=0.05)
        h = auto_align(h, template_height, threshold=0.1)
        x = auto_align(x, template_center_x, isCoord=True)
        y = auto_align(y, template_center_y, isCoord=True)
        header["width"] = w
        header["height"] = h
        coord = [x,y]
        header["coordinate"] = coord       
    
    # ensure same amount of distance between buttons
    template_distance_x = []
    headers.sort(key = lambda x:(x["coordinate"][1], x["coordinate"][0]))
    for i in range(len(headers)-1):
        if (headers[i+1]["coordinate"][1] == headers[i]["coordinate"][1]):
            d = headers[i+1]["coordinate"][0] - headers[i]["coordinate"][0]
            adjusted_d = auto_align(d, template_distance_x, threshold=0.05, isCoord=True)
            headers[i+1]["coordinate"][0] = headers[i]["coordinate"][0] + adjusted_d
    
    template_witdh = []
    template_height = []
    template_center_x = []
    template_center_y = []
    for header in headers:
        coord = header["coordinate"]
        w = header["width"]
        h = header["height"]
        x = coord[0]
        y = coord[1]
        w = auto_align(w, template_witdh, threshold=0.05)
        h = auto_align(h, template_height, threshold=0.1)
        x = auto_align(x, template_center_x, isCoord=True)
        y = auto_align(y, template_center_y, isCoord=True)
        header["width"] = w
        header["height"] = h
        coord = [x,y]
        header["coordinate"] = coord  
    
    return {
        "label": cleaned_result,
        "header": headers
    }

def export_eh(event, file_path):
    print(file_path)
    def to_export_label_dict(label: Label, result_dict, headers):
        valid = True
        result = label.basic_properties
        
        result['coordinate'] = label.center
        result['width'] = label.abs_width
        result['height'] = label.abs_height
        if result['type'] == 1:
            result_type = 'component'
        elif result['type'] == 2:
            result_type = 'databox'
        elif result['type'] == 3:
            result_type = 'button'
        elif result['type'] == 4:
            result_type = 4
        else:
            raise AssertionError()
        
        if result_type == 4:
            required_properties = {
                "name": result["name"],
                "coordinate":result["coordinate"],
                "width":result["width"],
                "height":result["height"],
                "isButton":result["isButton"],
                "isTime":result["isTime"],
            }
            headers.append(required_properties)
            return valid
        
        result_name = result["parent"]
        
        level = []
        if result["l"]:
            level.append("L")
        if result["ll"]:
            level.append("LL")
        if result["h"]:
            level.append("H")

        if result_name not in result_dict:
            result_dict[result_name] = {}
                        
        required_properties = {
            "name":result["name"],
            "desc":result["desc"],
            "status":result["status"],
            "state":result["state"],
            "component_type":result["component_type"],
            "flip":result["flip"],
            "rotation":result["rotation"],
            "coordinate":result["coordinate"],
            "width":result["width"],
            "height":result["height"],
            "level":level,
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
    headers = []
    for label in labels:
        if not to_export_label_dict(label, result, headers):
            return
    cleaned_result = convert_json(result, headers)
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
             sg.B('New Project', key='-NEW-'), sg.B('Open Existing Project', key='-OPEN-'), sg.B('Show/Hide connections', key='connections', visible=False)],
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

         sg.SaveAs('Export Connections', key='-EXPORT-CONN-', file_types=(('JSON file', '*.json'),),
                   target='export-conn-filename', visible=False),

         sg.B('New Project', key='-NEW-'), sg.B('Open Existing Project',
                                        key='-OPEN-'), sg.B('Show/Hide Connections', key='-CONN-', visible=False),

         sg.B('Label Pair', key='-CREATE-'),
         sg.SaveAs('Export', key='-EXPORT-', file_types=(('JSON file', '*.json'),),
                   target='export-filename'),
         sg.B('Label Header', key='-HEADER-'),
         sg.B('Return', key='-RETURN-', visible=False),
         
         ]
    ]

    if project_path is not None:
        os.chdir(project_path)
    window = sg.Window("Workplace", layout, finalize=True,
                       return_keyboard_events=True, resizable=True,
                       location=(0,0))

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
            
    def label_header(event):
        if global_pair_property.header == True:
            global_pair_property.header = False
        else:
            global_pair_property.header = True

    window_manager.register_handler('-NEW-', NewProjectEH())
    window_manager.register_handler('-OPEN-', OpenProjectEH())
    window_manager.register_handler('export-filename', export_eh)
    window_manager.register_handler('-CONN-', toggle_connections)
    window_manager.register_handler('export-conn-filename', export_conn_eh)
    window_manager.register_handler('-CREATE-', NewPairEH(graph_manager.handler))
    window_manager.register_handler('-HEADER-', label_header)
    window_manager.register_handler('-RETURN-', return_to_create_new)
    window_manager.run()


if __name__ == '__main__':
    show_workspace('')
