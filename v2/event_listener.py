from abc import ABC, abstractmethod


class EventListener(ABC):
    def __init__(self):
        self.component = None

    def set_component(self, component):
        self.component = component

    @abstractmethod
    def check(self, event, values):
        ...

    @abstractmethod
    def apply(self, event, values):
        ...


class EventListenerGroup:
    def __init__(self):
        self.component = None
        self.listeners = []

    def set_component(self, component):
        self.component = component

    def add_listener(self, listener):
        listener.set_component(self.component)
        self.listeners.append(listener)

    def apply(self, event, values):
        for listener in self.listeners:
            if listener.check(event, values) is True:
                listener.apply(event, values)
                return listener
        return None


class ContinuousEventListener(EventListener, ABC):
    def stop(self):
        ...


class ContinuousEventListenerGroup(EventListenerGroup):
    def __init__(self):
        super().__init__()
        self.active_listener = None

    def apply(self, event, values):
        if self.active_listener is None:
            self.active_listener = super().apply(event, values)
        else:
            self.active_listener.apply(event, values)

        return self.active_listener

    def stop(self):
        self.active_listener.stop()
        self.active_listener = None
