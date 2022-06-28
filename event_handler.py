from abc import ABC


class EventHandler(ABC):
    def process(self):