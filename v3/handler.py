from abc import abstractmethod, ABC
from typing import Callable

import PySimpleGUI as sg

from event import Event


class View(ABC):

    def draw(self, graph: sg.Graph, *args, **kwargs):
        self.clear(graph, *args, **kwargs)

        self._draw(graph, *args, **kwargs)

    def clear(self, graph: sg.Graph, *args, **kwargs):
        self._clear(graph, *args, **kwargs)

    @abstractmethod
    def _draw(self, graph):
        ...

    @abstractmethod
    def _clear(self, graph):
        ...


class Handler(ABC):

    @abstractmethod
    def handle(self, e: Event):
        ...


class SimpleHandler(Handler):
    def __init__(self, callback: Callable):
        self.callback = callback

    def handle(self, e: Event):
        self.callback(e)


class Filter(ABC):
    @abstractmethod
    def filter(self, e: Event) -> Event | None:
        ...


class SequenceHandler(Handler):
    @abstractmethod
    def start(self, e: Event):
        ...

    @abstractmethod
    def stop(self, e: Event):
        ...


class FilteredHandler(Handler):
    def __init__(self, f: Filter, h: Handler):
        self._filter = f
        self._handler = h

    def filter(self, e: Event):
        return self._filter.filter(e)

    def handle(self, e: Event):
        self._handler.handle(self.filter(e))


class FilteredSequenceHandler(SequenceHandler):
    def __init__(self, f: Filter, h: SequenceHandler):
        self._filter = f
        self._handler = h

    def filter(self, e: Event):
        return self._filter.filter(e)

    def start(self, e: Event):
        self._handler.start(self.filter(e))

    def handle(self, e: Event):
        self._handler.handle(e)

    def stop(self, e: Event):
        self._handler.stop(e)


class HandlerChain(Handler):
    def __init__(self):
        self.handlers: list[FilteredHandler] = []

    def add_handler(self, h: FilteredHandler):
        self.handlers.append(h)

    def handle(self, e: Event):
        for h in self.handlers:
            if h.filter(e):
                h.handle(e)
                break


class SequenceHandlerChain(SequenceHandler):
    def __init__(self):
        self.active_handler: SequenceHandler | None = None
        self.handlers: list[FilteredSequenceHandler] = []

    def add_handler(self, h: FilteredSequenceHandler):
        self.handlers.append(h)

    def start(self, e: Event):
        print('start SC')
        for h in self.handlers:
            if h.filter(e):
                print('active handler', h._handler, h._filter, h.filter(e))
                self.active_handler = h
                self.active_handler.start(e)
                break

    def handle(self, e: Event):
        print('handle SC')
        self.active_handler.handle(e)

    def stop(self, e: Event):
        print('stop SC')
        self.active_handler.stop(e)


class EmptyHandler(Handler):
    def handle(self, e: Event):
        pass


class EmptySequenceHandler(SequenceHandler):
    def start(self, e: Event):
        pass

    def handle(self, e: Event):
        pass

    def stop(self, e: Event):
        pass


class DefaultFilter(Filter):
    def filter(self, e: Event) -> Event | None:
        return e
