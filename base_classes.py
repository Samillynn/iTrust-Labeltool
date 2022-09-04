from abc import ABC, abstractmethod


class Serializer(ABC):
    @abstractmethod
    def serialize(self, obj):
        ...

    @abstractmethod
    def deserialize(self, data):
        ...


class EventHandler(ABC):
    @abstractmethod
    def react(self):
        ...


class Event:
    def __init__(self, name=None, value=None, target=None):
        self.name: str = name
        self.value = value
        self.target = target

    def __repr__(self):
        return f'Event{(self.name, self.value, self.target)}'

    def clone(self):
        return self.__class__(self.name, self.value, self.target)
