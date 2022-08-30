import functools
from time import sleep
from typing import Collection

from event import Event
from handler import Handler, SequenceHandler, FilteredHandler, Filter, SequenceHandlerChain, FilteredSequenceHandler, \
    HandlerChain, View, DefaultFilter
from label import Label, LabelView
from utils import Vector, Vertex
from v3.app_state import Keys, window_state
from v3.cursor_handler import CursorHandler
from v3.dialogs import new_label_dialog, update_label_dialog
from v3.session_storage import SessionStorage, Image, ImageView


def vectorize_value(handle):
    @functools.wraps(handle)
    def wrapper(self, e):
        e.value = Vector(e.value)
        return handle(self, e)
    return wrapper


class DisplacementDecorator(SequenceHandler):
    def __init__(self, handler: SequenceHandler):
        self.handler = handler
        self.prev_position: Vector | None = None

    def start(self, e: Event):
        self.prev_position = e.value
        self.handler.start(e)

    def handle(self, e: Event):
        position = e.value
        displacement = position - self.prev_position
        self.prev_position = position

        e.value = displacement
        self.handler.handle(e)

    def stop(self, e: Event):
        position = e.value
        displacement = position - self.prev_position
        self.prev_position = position

        e.value = displacement
        self.handler.stop(e)


class DuplicateLabelHandler(SequenceHandler):
    def __init__(self):
        self.label: Label = Label()

    def start(self, e: Event):
        graph_controller = e.target
        self.label = graph_controller.focus
        graph_controller.add_label(self.label.clone())

    def handle(self, e: Event):
        displacement = Vector(e.value)
        self.label.move(displacement)

    def stop(self, e: Event):
        pass


class UpdateLabelHandler(Handler):
    def handle(self, e: Event):
        graph_controller = e.target
        label = e.target.focus

        update_e = update_label_dialog(label)
        match update_e.name:
            case 'Delete':
                graph_controller.labels.remove(label)
            case 'Update':
                label_info = update_e.value
                label.name = label_info['name']
                label.category = label_info['category']
                label.text = label_info['text']
            case 'Cancel' | None:
                ...
            case _:
                raise AssertionError(e)


class MoveLabelHandler(SequenceHandler):
    def __init__(self):
        self.label: Label = Label()

    def start(self, e: Event):
        self.label = e.target.focus

    def handle(self, e: Event):
        displacement = Vector(e.value[0], e.value[1])
        self.label.move(displacement)

    def stop(self, e: Event):
        pass


class MoveVertexHandler(SequenceHandler):
    def __init__(self):
        self.vertex: Vertex = Vertex()

    def start(self, e: Event):
        self.vertex = e.target.focus

    def handle(self, e: Event):
        self.vertex.position += e.value

    def stop(self, e: Event):
        pass


class NewLabelHandler(SequenceHandler):
    def __init__(self):
        self.label: Label = Label()
        self.vertex: Vertex = Vertex()

    def start(self, e: Event):
        position = e.value
        graph_controller = e.target

        self.label = Label(start=position, end=position)
        self.vertex = self.label.bottom_right
        graph_controller.add_label(self.label)

    def handle(self, e: Event):
        self.vertex.position += e.value

    def stop(self, new_label_e: Event):
        new_label_e = new_label_dialog()
        if new_label_e.name in ['Submit']:
            self.label.name = new_label_e.value['name']
            self.label.category = new_label_e.value['category']
            self.label.text = new_label_e.value['text']
        elif new_label_e.name in ['Exit', None]:
            new_label_e.target.labels.remove(self.label)
            pass
        else:
            raise AssertionError(new_label_e)


class NearbyVertexFilter(Filter):
    def filter(self, e: Event) -> Event | None:
        graph_controller = e.target
        position = e.value

        for label in graph_controller.labels:
            if vertex := label.nearby_vertex(position):
                graph_controller.focus = vertex
                return e

        return None


class InsideLabelFilter(Filter):
    def filter(self, e: Event) -> Event | None:
        graph_controller = e.target
        position = e.value

        for label in graph_controller.labels:
            if label.includes(position):
                graph_controller.focus = label
                return e

        return None


class KeyPressedFilter(Filter):
    def __init__(self, required_key: Keys, prev_filter: Filter):
        self.required_key: Keys = required_key
        self.prev_filter: Filter = prev_filter

    def filter(self, e: Event) -> Event | None:
        if window_state.key_pressed(self.required_key):
            return self.prev_filter.filter(e)
        else:
            return None


class CursorShapeHandler(Handler):
    def __init__(self):
        self.filter: dict[str, Filter] = {
            'near_vertex': NearbyVertexFilter(),
            'inside_label': InsideLabelFilter(),
        }
        self.shape = {
            'near_vertex': 'cross',
            'inside_shape': 'fleur',
            'default': 'arrow'
        }

    def handle(self, e: Event):
        component = e.target
        for situation in ['near_vertex', 'inside_shape']:
            if self.filter[situation].filter(e):
                component.set_cursor(self.shape[situation])
                break
        else:
            component.set_cursor(self.shape['default'])


class GraphController(Handler):

    def __init__(self, storage: SessionStorage):
        self.storage: SessionStorage = storage
        self.focus = None
        self.labels: list[Label] = list(self.storage.labels)
        self.image = Image(self.storage.image_path)
        print('init', self.image)

        self.cursor_handler = CursorHandler()

        self.init_on_hover()
        self.init_on_click()
        self.init_on_drag()

    @vectorize_value
    def handle(self, e: Event):
        self.cursor_handler.handle(e)

    def init_on_click(self):
        click_handler = HandlerChain()
        click_handler.add_handler(FilteredHandler(InsideLabelFilter(), UpdateLabelHandler()))

        self.cursor_handler.click_handler = click_handler

    def init_on_hover(self):
        self.cursor_handler.hover_handler = CursorHandler()

    def init_on_drag(self):
        drag_handler = SequenceHandlerChain()

        move_vertex_handler = FilteredSequenceHandler(NearbyVertexFilter(), MoveVertexHandler())
        drag_handler.add_handler(move_vertex_handler)

        move_label_handler = FilteredSequenceHandler(InsideLabelFilter(), MoveLabelHandler())
        drag_handler.add_handler(move_label_handler)

        duplication_filter = KeyPressedFilter(Keys.CONTROL, InsideLabelFilter())
        duplicate_label_handler = FilteredSequenceHandler(duplication_filter, DuplicateLabelHandler())
        drag_handler.add_handler(duplicate_label_handler)

        new_label_handler = FilteredSequenceHandler(DefaultFilter(), NewLabelHandler())
        drag_handler.add_handler(new_label_handler)

        self.cursor_handler.drag_handler = DisplacementDecorator(drag_handler)

    def save_to_storage(self):
        self.storage.image = self.image
        self.storage.labels = self.labels

    def add_label(self, label: Label):
        self.labels.append(label)


class GraphView(View):
    def __init__(self, image=None, labels=None):
        super().__init__()
        self.image: Image = Image()
        self.labels: list[Label] = []

        if image:
            self.image = image
        if labels:
            self.labels = labels

        self.label_views: list[LabelView] = []
        self.image_view: ImageView | None = None

    def _clear(self, graph, image=False):
        if image is True and self.image_view:
            self.image_view.clear(graph)
            self.image_view = None

        for label_view in self.label_views:
            label_view.clear(graph)
            self.label_views.clear()

    def _draw(self, graph, image=True):
        if image is True:
            self.clear(graph, image=True)
            graph.set_size(self.image.size)

            self.image_view = ImageView(self.image)
            self.image_view.draw(graph)

        for label in self.labels:
            label_view = LabelView(label)
            label_view.draw(graph)
            self.label_views.append(label_view)


if __name__ == '__main__':
    class MockStorage(SessionStorage):

        @property
        def image_path(self) -> str:
            return 'screen_shot.jpg'

        @property
        def labels(self) -> Collection[Label]:
            return []


    graph_controller = GraphController(MockStorage())
    print(graph_controller)

    # # new label
    # new_label_handler = NewLabelHandler()
    # new_label_handler.start(Event('', (1, 1), graph_controller))
    # print(graph_controller.labels)
    # new_label_handler.handle(Event('', (1, 3), graph_controller))
    # print(graph_controller.labels)
    # new_label_handler.stop(Event())
    # print(graph_controller.labels[-1].name)
    #
    # # update label
    # update_label_handler = UpdateLabelHandler()
    # graph_controller.focus = graph_controller.labels[-1]
    # update_label_handler.handle(Event('', '', graph_controller))
    #
    # # move label
    # move_label_handler = MoveLabelHandler()
    # graph_controller.focus = graph_controller.labels[-1]
    # move_label_handler.start(Event('', (1, 1), graph_controller))
    # move_label_handler.handle(Event('', (1, 1), graph_controller))
    # move_label_handler.stop(Event())
    #
    # # resize
    # move_vertex_handler = MoveVertexHandler()
    # graph_controller.focus = graph_controller.labels[-1].top_right
    # move_vertex_handler.start(Event('', '', graph_controller))
    # move_vertex_handler.handle(Event('', (100, 100), graph_controller))
    # move_vertex_handler.stop(Event())

    # duplicate
    # duplicate_handler = DuplicateLabelHandler()
    # graph_controller.focus = graph_controller.labels[-1]
    # duplicate_handler.start(Event(target=graph_controller))
    # duplicate_handler.handle(Event(value=(-100, -100), target=graph_controller))
    # duplicate_handler.stop(Event())
    # print(graph_controller.labels)

    # new label
    graph_controller.handle(Event('', (1, 1), graph_controller))
    sleep(0.6)
    graph_controller.handle(Event('', (10, 10), graph_controller))
    graph_controller.handle(Event('+UP', (10, 10), graph_controller))
    print(graph_controller.labels)

    sleep(0.6)
    # update
    graph_controller.handle(Event('', (1, 1), graph_controller))
    graph_controller.handle(Event('+UP', (1, 1), graph_controller))
    print(graph_controller.labels)

    # resize
    graph_controller
