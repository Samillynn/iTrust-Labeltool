import copy
from typing import TYPE_CHECKING

import modifier_key
from pair_property import global_pair_property, NewPairEH, assign_current_choice
from utils import sg
from .dialog import BaseDialog
from .label import Label, LabelSerializer
from config import config
from utils import preprocess
from pytesseract import pytesseract

if TYPE_CHECKING:
    from .graph_handler import GraphHandler


class DragHandler:
    def __init__(self, graph_handler):
        self.graph_handler: GraphHandler = graph_handler

    def start(self, position) -> bool:
        return False

    def handle(self, displacement):
        ...

    def stop(self):
        ...


class DragHandlerChain:
    def __init__(self):
        self.handlers: list[DragHandler] = []
        self.active_handler: DragHandler | None = None

    def add_handler(self, handler: DragHandler):
        self.handlers.append(handler)

    def start(self, position) -> bool:
        for handler in self.handlers:
            if handler.start(position):
                self.active_handler = handler
                return True
        return False

    def handle(self, displacement):
        assert self.active_handler is not None
        self.active_handler.handle(displacement)

    def stop(self):
        assert self.active_handler is not None
        self.active_handler.stop()

        self.active_handler = None


class NewLabelHandler(DragHandler):
    def __init__(self, graph_handler):
        self.label = None
        self.dialog = None
        super().__init__(graph_handler)
        
    @staticmethod
    def select_list(title, choices):
        return sg.Tab(title, [[sg.Listbox(choices, s=(40, 20), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, enable_events=True, key=f'list-{title}')]])

    def start(self, position):
        # if self.graph_handler.hovered_label(position) or self.graph_handler.nearby_vertex(position):
        if self.graph_handler.hovered_label(position):
            return False

        self.label = Label(position, position)
        self.dialog = BaseDialog(self.label)
        self.graph_handler.add_label(self.label)

        self.graph_handler.graph.set_cursor("cross")
        return True

    def handle(self, displacement):
        self.label.move_vertex('bottom_right', displacement)
        self.graph_handler.notify_labels()

    def stop(self):
        self.label.parent_component_name = self.graph_handler.pair_parent_name
        self.label._type = self.graph_handler.pair_type

        self.ask_label_info()
        self.graph_handler.notify_labels()
        self.graph_handler.graph.set_cursor('arrow')

        self.label = None

        if global_pair_property.current_choice is not None:
            # self.graph_handler.image.add_shadow()
            # self.graph_handler.notify_image()
            handler = NewPairEH(self.graph_handler)
            handler.handle()


    def component_layout(self):
        base_dialog = BaseDialog()
        name_str = global_pair_property.name + " " + "component"
        if global_pair_property.name in ["", None]:
            name_str = ""
        left_l = [
            [sg.T("Parent"), sg.I(key='parent', default_text=global_pair_property.name)],
            [sg.T("Type"), sg.I(key='component_type', default_text=global_pair_property.component_type)],
            [sg.T("Name"), sg.I(key='name', default_text=name_str)],
            [sg.T("Description"), sg.I(key="desc", default_text=global_pair_property.desc)],
            [sg.T("Status"), sg.I(key="status", default_text=global_pair_property.status)],
            [sg.T("State"), sg.I(key="state", default_text=global_pair_property.state)],
            base_dialog.layout_level(),
            base_dialog.layout_flip(),
            base_dialog.layout_rotation(),
            # [sg.T('Category'), sg.DD(config["categories"],key='category')],
            [sg.T("Coordinate"), sg.T(
                f"x: {self.label.center_x}; y: {self.label.center_y}")],
            [sg.Submit(), sg.Exit()]
        ]
        # cropped img
        cropped_img = self.graph_handler.image.crop_for_ocr(self.label)
        # process img
        img = preprocess(cropped_img)
        
        lst = list(filter(bool, pytesseract.image_to_string(
            img, config=config["tesseract_config"]).split('\n')))
        right_layout = [[sg.TabGroup(
            [[self.select_list('name', lst), self.select_list('description', lst)]])]]
        layout = [[sg.Column(left_l), sg.VSep(), sg.Column(right_layout)]]


        return layout

    def component_dialog(self):
        self.dialog.create('Component', self.component_layout())
        return self.dialog.read(close=False)
    
    def header_layout(self):
        layout = [
            [sg.T("Name"), sg.I(key='name', default_text="")],
            [sg.Checkbox('isButton', key='isButton')],
            [sg.T("Coordinate"), sg.T(
                f"x: {self.label.center_x}; y: {self.label.center_y}")],
            [sg.Submit(), sg.Exit()]
        ]
        return layout

    def databox_layout(self):
        name_str = global_pair_property.name + " " + "databox"
        if global_pair_property.name in ["", None]:
            name_str = ""
        layout = [
            [sg.T("Parent"), sg.I(key='parent', default_text=global_pair_property.name)],
            [sg.T("Type"), sg.I(key='component_type', default_text=global_pair_property.component_type)],
            [sg.T("Name"), sg.I(key='name', default_text=name_str)],
            [sg.T("Description"), sg.I(key="desc", default_text=global_pair_property.desc)],
            [sg.T("Status"), sg.I(key="status", default_text=global_pair_property.status)],
            [sg.T("State"), sg.I(key="state", default_text=global_pair_property.state)],
            [sg.T("Coordinate"), sg.T(
                f"x: {self.label.center_x}; y: {self.label.center_y}")],
            [sg.Submit(), sg.Exit()]
        ]

        return layout
    
    def header_dialog(self):
        self.dialog.create("Header", self.header_layout())
        return self.dialog.read(close=False)

    def databox_dialog(self):
        self.dialog.create('Databox', self.databox_layout())
        return self.dialog.read(close=False)
    
    def button_dialog(self):
        self.dialog.create('Button', self.databox_layout())
        return self.dialog.read(close=False)
    
    def new_label_dialog(self):
        layout = self.dialog.layout(enable_event=False)
        layout += [[sg.Submit(), sg.Exit()]]
        self.dialog.create('Create new label', layout)
        return self.dialog.read(close=False)

    def ask_label_info(self):

        # whether a component or a databox is currently labeled
        current_choice = global_pair_property.current_choice
        labeling_header = global_pair_property.header
        if current_choice is None:
            if not labeling_header:
                event, values = self.new_label_dialog()
            else:
                event, values = self.header_dialog()
                values["type"] = 4
        elif current_choice == 'Component':
            event, values = self.component_dialog()
            values["type"] = 1
        elif current_choice == "Databox":
            event, values = self.databox_dialog()
            values["type"] = 2
        elif current_choice == "Button":
            event, values = self.button_dialog()
            values["type"] = 3
        else:
            raise AssertionError
        
        while True:
            if current_choice == 'Component':
                values["type"] = 1
            elif current_choice == "Databox":
                values["type"] = 2
            elif current_choice == "Button":
                values["type"] = 3
            if event in ['Submit']:
                self.label.copy_basic_properties(values)
                if global_pair_property.choosing:
                    global_pair_property.name = self.label.parent
                    global_pair_property.component_type = self.label.component_type
                    global_pair_property.status = self.label.status
                    global_pair_property.state = self.label.state
                    global_pair_property.desc = self.label.desc
                    if self.label.type == 1:
                        global_pair_property.l = values["l"]
                        global_pair_property.ll = values["ll"]
                        global_pair_property.h = values["h"]
                        global_pair_property.flip = values["flip"]
                        global_pair_property.rotation = values["rotation"]
                if global_pair_property.current_choice is not None:
                    assign_current_choice(self.label)
                break
                    
            elif event in ['Exit', None]:
                self.graph_handler.labels.remove(self.label)
                if global_pair_property.current_choice is not None:
                    assign_current_choice(None)
                break
            
            elif event == 'list-description':
                val = values['list-description']
                self.dialog.window['name'].update(' '.join(val))
            elif event == 'list-name':
                val = values['list-name']
                self.dialog.window['parent'].update(' '.join(val))
            else:
                raise AssertionError(event)
            event, values = self.dialog.read(close=False)
        self.dialog.close()

class MoveLabelHandler(DragHandler):
    def __init__(self, graph_handler):
        super().__init__(graph_handler)
        self.label = None

    def start(self, position):
        if label := self.graph_handler.hovered_label(position):
            self.label = label
            return True

        return False

    def handle(self, displacement):
        if global_pair_property.choosing == False:
            self.label.move(displacement)
            self.graph_handler.notify_labels()


class MoveVertexHandler(DragHandler):
    def __init__(self, graph_handler):
        super().__init__(graph_handler)
        self.label = None
        self.vertex_name = ''

    def start(self, position):
        if self.graph_handler.hovered_label(position):
            if nearby := self.graph_handler.nearby_vertex(position):
                self.label, self.vertex_name = nearby
                return True

        return False

    def handle(self, displacement):
        if global_pair_property.choosing == False:
            self.label.move_vertex(self.vertex_name, displacement)
            self.graph_handler.notify_labels()


class DuplicateLabelHandler(DragHandler):
    def __init__(self, graph_handler):
        self.label = None
        super().__init__(graph_handler)

    def start(self, position):
        if (label := self.graph_handler.hovered_label(position)) and modifier_key.ctrl:
            self.label = copy.deepcopy(label)
            self.graph_handler.add_label(self.label)
            return True

        return False

    def handle(self, displacement):
        if global_pair_property.choosing == False:
            self.label.move(displacement)
            self.graph_handler.notify_labels()
