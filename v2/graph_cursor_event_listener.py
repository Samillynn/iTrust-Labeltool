from utils import current_milli_time, Point
from v2.event_listener import EventListener, EventListenerGroup, ContinuousEventListenerGroup


class GraphCursorEventListener(EventListener):
    def check(self, event, values):
        return event.startswith('-GRAPH-')

    def __init__(self):
        super().__init__()
        self.mouse_down = False
        self.mouse_down_time = None

        self.hover_listeners = EventListenerGroup()
        self.click_listeners = EventListenerGroup()
        self.drag_listeners = ContinuousEventListenerGroup()

    def set_component(self, component):
        self.hover_listeners.set_component(component)
        self.click_listeners.set_component(component)
        self.drag_listeners.set_component(component)

    def apply(self, event, values):
        if not event.startswith('-GRAPH-'):
            return False

        point = Point(values)
        if event.endswith('+MOVE'):
            self.hover_listeners.apply(event, values)
        elif event.endswith('+UP'):
            if current_milli_time() - self.mouse_down_time <= 100:
                self.click_listeners.apply(event, values)
            else:
                self.drag_listeners.stop()
        else:
            if self.mouse_down is False:
                self.mouse_down = True
                self.mouse_down_time = current_milli_time()
            else:
                if current_milli_time() - self.mouse_down_time > 100:
                    self.drag_listeners.apply(event, values)
                else:
                    pass  # wait time to escape

    def add_hover_listener(self, listener):
        self.hover_listeners.add_listener(listener)

    def add_click_listener(self, listener):
        self.click_listeners.add_listener(listener)

    def add_drag_listener(self, listener):
        self.drag_listeners.add_listener(listener)
