from enum import Enum

from v3.event import Event


class Keys(Enum):
    CONTROL = 1


class WindowState:
    def __init__(self, window=None):
        self.pressed_keys = set()
        self.window = window

    def key_pressed(self, key: Keys):
        return key in self.pressed_keys

    @property
    def cursor_shape(self):
        raise NotImplemented('Getting cursor shape is not implemented.')

    @cursor_shape.setter
    def cursor_shape(self, shape: str):
        self.window.set_cursor(cursor=shape)

    def trace(self, e: Event):
        match e.name:
            case 'Control-KeyPress':
                self.pressed_keys.add(Keys.CONTROL)
            case 'Control*':
                self.pressed_keys.remove(Keys.CONTROL)


window_state = WindowState()
