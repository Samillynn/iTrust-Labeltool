from event import Event
from handler import Handler, EmptyHandler, EmptySequenceHandler
from utils import current_milli_time


class CursorHandler(Handler):

    def __init__(self):
        self.click_threshold = 100
        self.mouse_down_time = None
        self.is_dragging = False

        self.hover_handler = EmptyHandler()
        self.click_handler = EmptyHandler()
        self.drag_handler = EmptySequenceHandler()
        self.pending_events: list[Event] = []

    def long_mouse_down(self):
        return current_milli_time() - self.mouse_down_time > self.click_threshold

    def handle(self, e: Event):
        if e.name.endswith('+MOVE'):
            self.hover_handler.handle(e)

        elif e.name.endswith('+UP'):
            if self.is_dragging:
                print('stop dragging')
                self.drag_handler.stop(e)
            else:
                print('click')
                self.click_handler.handle(e)
            self.mouse_down_time = None
            self.is_dragging = False

        else:
            if not self.mouse_down_time:
                print('start pending')
                self.mouse_down_time = current_milli_time()
                self.pending_events.append(e)
            elif self.long_mouse_down():
                if self.is_dragging:
                    print('dragging')
                    self.drag_handler.handle(e)
                else:
                    print('start dragging')
                    self.is_dragging = True

                    self.pending_events.append(e)
                    self.drag_handler.start(self.pending_events[0])
                    for pending_e in self.pending_events[1:]:
                        self.drag_handler.handle(pending_e)
            else:
                print('pending')
                self.pending_events.append(e)

