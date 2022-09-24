from base_classes import EventHandler


class HandlerChain:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__handlers = []

    def add_handler(self, handler):
        if callable(handler):
            self.__handlers.append(handler)
        elif isinstance(handler, EventHandler):
            self.__handlers.append(handler.handle)
        else:
            raise ValueError(f'The handler added either have "handle" method or be callable: {handler}')

    def handle(self, *args, **kwargs):
        for handler in self.__handlers:
            if handler(*args, **kwargs):
                return True

        return False
