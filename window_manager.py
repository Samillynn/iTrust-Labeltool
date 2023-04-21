import logging
import time

from base_classes import EventHandler
from handler_chain import HandlerChain
from utils import sg
from pair_property import global_pair_property

logging.basicConfig(level=logging.INFO)


class WindowManager(HandlerChain):

    def __init__(self, window):
        super().__init__()
        self.window: sg.Window = window
        self.event = None
        self.values = None
        self.close = False

        self.win_close_handler = None
        self.handlers = {}

    def _register_single_handler(self, key, handler):
        assert isinstance(key, str)
        if key in self.handlers:
            self.handlers[key].append(handler)
        else:
            self.handlers[key] = [handler]

    def register_handler(self, key, handler):
        if isinstance(key, str):
            self._register_single_handler(key, handler)
        elif isinstance(key, list):
            # TODO: more general types
            for one_key in key:
                self._register_single_handler(one_key, handler)

    def run(self, close=False):
        while True:
            if global_pair_property.choosing:
                self.window["-RETURN-"].update(visible=True)
            else:
                self.window["-RETURN-"].update(visible=False)
            if global_pair_property.header:
                self.window['-HEADER-'].update(button_color=('white', 'green'))
            else:
                self.window['-HEADER-'].update(button_color=sg.theme_button_color())
                

            self.event, self.values = self.window.read(close=close)
            # logging.info(f'event: {self.event}, values: {self.values}')

            self.handle(self.event, self.values)

            if self.event in (sg.WIN_X_EVENT,):
                if self.win_close_handler is None:
                    self.window.close()

                self.win_close_handler.process()
                if self.close:
                    self.window.close()

            # if self.event is None:
            #     break
            
            for key, key_handlers in self.handlers.items():
                if self.event.startswith(key):
                    for handler in key_handlers:
                        try:
                            values = self.values[key]
                        except KeyError:
                            values = self.values

                        if isinstance(handler, EventHandler):
                            callback = handler.handle
                        elif callable(handler):
                            callback = handler
                        else:
                            raise TypeError('Handler is either an EventHandler instance or an callable.')

                        try:
                            callback(self.event.removeprefix(key), values)

                        except TypeError:
                            try:
                                callback(self.event)
                            except TypeError:
                                callback()
