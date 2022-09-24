import modifier_key
from graph.graph_handler import GraphHandler, GraphView
from graph.label_history import LabelHistory
from session_storage import JsonSessionStorage


class GraphManager:
    def __init__(self, graph, json_path='session.json'):
        self.storage = JsonSessionStorage(json_path)

        self.handler = GraphHandler(graph=graph, image_path=self.storage.image_path, labels=self.storage.labels)
        self.handler.add_observer(self.update_storage)

        self.view = GraphView(graph)
        self.handler.add_observer(self.update_view)

        # window resize
        self.handler.add_handler(self.handle_resize_window)

        # undo/redo
        self.init_label_history()

        self.handler.start()

    def init_label_history(self):
        # label history to undo/redo
        label_history = LabelHistory()

        def new_label_action(event, labels):
            if event == 'labels':
                label_history.add_state(labels)

        self.handler.add_observer(new_label_action)

        def undo_by_ctrl_z(event, values):
            if (event == 'z' or event.startswith('z:')) and modifier_key.ctrl:
                if prev_labels := label_history.undo():
                    self.handler.labels = prev_labels
                    self.handler.notify_labels()
                return True
            return False

        def redo_by_ctrl_r(event, values):
            if event == 'r' and modifier_key.ctrl:
                if next_labels := label_history.redo():
                    self.handler.labels = next_labels
                    self.handler.notify_labels()
                return True
            return False

        self.handler.add_handler(undo_by_ctrl_z)
        self.handler.add_handler(redo_by_ctrl_r)

    def handle_resize_window(self, event, values):
        if modifier_key.ctrl:
            if event.startswith('equal') or event == '=':
                self.handler.image.resize += 0.1
                self.handler.notify_image()
                return True
            elif event.startswith('minus') or event == '-':
                if self.handler.image.resize >= 0.1:
                    self.handler.image.resize -= 0.1
                    self.handler.notify_image()
                return True
        return False

    def update_view(self, event, values):
        if event == 'labels':
            labels = values
            self.view.labels = labels

        elif event == 'image':
            image = values
            self.view.image = image

    def update_storage(self, event, values):
        if event == 'labels':
            labels = values
            self.storage.labels = labels

        elif event == 'image':
            image = values
            self.storage.image = image

    def handle(self, event, values):
        self.handler.handle(event, values)
