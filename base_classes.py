from typing import Protocol, runtime_checkable


@runtime_checkable
class Serializer(Protocol):
    def serialize(self, obj): ...

    def deserialize(self, data): ...


@runtime_checkable
class EventHandler(Protocol):
    def handle(self, *args, **kwargs) -> bool: ...


class Event:
    def __init__(self, name=None, value=None, target=None):
        self.name: str = name
        self.value = value
        self.target = target

    def __repr__(self):
        return f'Event{(self.name, self.value, self.target)}'

    def copy(self):
        return self.__class__(self.name, self.value, self.target)
