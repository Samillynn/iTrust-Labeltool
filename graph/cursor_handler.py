from typing import Any

from utils import current_milli_time


class CursorHandler:
    HOVER = 0
    CLICK = 1
    DRAG_START = 2
    DRAG_HANDLE = 3
    DRAG_STOP = 4
    SELECT = 5


    def __init__(self):
        self.click_threshold = 100
        self.mouse_down_time = None
        self.is_dragging = False
        self.prev_click = 0
        self.click_num = 0
        self.pending_events = []

    def long_mouse_down(self):
        return current_milli_time() - self.mouse_down_time > self.click_threshold

    def handle(self, event, values) -> list[(int, Any)]:
        if event.endswith('+MOVE'):
            return [(self.HOVER, values)]

        if event.endswith('+UP'):
            self.pending_events.clear()
            self.mouse_down_time = None
            current = current_milli_time()
            print(current, self.prev_click)

            if self.is_dragging:
                self.is_dragging = False
                return [(self.DRAG_STOP, values)]
            elif current - self.prev_click < 300 and self.click_num == 1:
                print(values)
                return [(self.CLICK, values)]
            else:
                return [(self.SELECT, values)]


        if not self.mouse_down_time:
            # start pending
            current = current_milli_time()
            if current - self.prev_click < 300 and self.click_num == 0:
                self.click_num = 1
            else:
                self.click_num = 0
            self.mouse_down_time = current_milli_time()
            self.prev_click = current_milli_time()
            self.pending_events.append((self.DRAG_START, values))
            return []

        if self.long_mouse_down():
            if self.is_dragging:
                # dragging
                return [(self.DRAG_HANDLE, values)]
            else:
                # start dragging and stop pending
                self.is_dragging = True

                self.pending_events.append((self.DRAG_HANDLE, values))
                return list(self.pending_events)
        else:
            # pending
            self.pending_events.append((self.DRAG_HANDLE, values))
            return []
