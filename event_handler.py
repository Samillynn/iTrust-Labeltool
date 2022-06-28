from abc import ABC, abstractmethod


class EventHandler(ABC):
    @abstractmethod
    def react(self):
        ...
