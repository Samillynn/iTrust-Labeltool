import logging

from event_handler import EventHandler
from utils import sg
logging.basicConfig(level=logging.INFO)


class WindowManager:

    def __init__(self, window):
        self.window: sg.Window = window
        self.event = None
        self.values = None
        self.close = False

        self.win_close_handler = None
        self.handlers = {}

    def _register_single_handler(self, key, handler, keep_prefix):
        assert isinstance(key, str)
        if key in self.handlers:
            self.handlers[key].append((handler, keep_prefix))
        else:
            self.handlers[key] = [(handler, keep_prefix)]

    def register_x_handler(self, handler):
        self.win_close_handler = handler

    def register_handler(self, key, handler, keep_prefix=False):
        if isinstance(key, str):
            self._register_single_handler(key, handler, keep_prefix)
        elif isinstance(key, list):
            # TODO: more general types
            for one_key in key:
                self._register_single_handler(one_key, handler, keep_prefix)

    def run(self, close=False):
        while True:
            self.event, self.values = self.window.read(close=close)
            logging.info(f'event: {self.event}, values: {self.values}')

            if self.event in (sg.WIN_X_EVENT, ):
                if self.win_close_handler is None:
                    self.window.close()

                self.win_close_handler.process()
                if self.close:
                    self.window.close()

            if self.event is None:
                break
            for key, key_handlers in self.handlers.items():
                if self.event.startswith(key):
                    for handler, keep_prefix in key_handlers:
                        try:
                            values = self.values[key]
                        except KeyError:
                            values = self.values

                        if isinstance(handler, EventHandler):
                            callback = handler.react
                        elif callable(handler):
                            callback = handler
                        else:
                            raise TypeError('Handler is either an EventHandler instance or an callable.')

                        event = self.event
                        if not keep_prefix:
                            event = event.removeprefix(key)
                        try:
                            callback(event, values)

                        except TypeError:
                            callback()
