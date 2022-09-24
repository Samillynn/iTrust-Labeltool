from abc import abstractmethod
from typing import Protocol, runtime_checkable, Callable


@runtime_checkable
class Observer(Protocol):
    @abstractmethod
    def observe(*args, **kwargs):
        ...


class Observable:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__observers = []

    def add_observer(self, observer: Observer | Callable):
        if isinstance(observer, Observer) or callable(observer):
            self.__observers.append(observer)
        else:
            raise ValueError(f'The observer added must be an instance of Observer or callable: {observer}')

    def add_observers(self, observers):
        self.__observers.extend(list(observers))

    def notify(self, *args, **kwargs):
        for observer in self.__observers:
            if isinstance(observer, Observer):
                observer.observe(*args, **kwargs)
            elif callable(observer):
                observer(*args, **kwargs)
            else:
                raise AssertionError()
