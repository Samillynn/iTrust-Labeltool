import json
from abc import ABC, abstractmethod
from typing import Collection

import PySimpleGUI as sg

from label import Label
from v3.handler import View
from v3.utils import convert_to_bytes, get_image_size


class Image:
    def __init__(self, path: str = ''):
        self.path: str = path
        self.resize: tuple[float, float] = (1, 1)

    def __repr__(self):
        return f'{type(self).__name__}({self.path})'

    @property
    def data(self) -> bytes:
        if self.path:
            return convert_to_bytes(self.path, self.size)
        else:
            return b''

    @property
    def size(self) -> tuple[int, int]:
        width, height = get_image_size(self.path)
        return int(width * self.resize[0]), int(height * self.resize[1])


class ImageView(View):
    def __init__(self, image: Image):
        super().__init__()
        self.image = image
        self.figure: int = -1

    def _clear(self, graph: sg.Graph):
        graph.delete_figure(self.figure)

    def _draw(self, graph: sg.Graph, location=(-1, 1)):
        graph.draw_image(data=self.image.data, location=location)


class SessionStorage(ABC):

    @property
    @abstractmethod
    def image_path(self) -> str:
        ...

    @image_path.setter
    @abstractmethod
    def image_path(self, image_path: str):
        ...

    @property
    @abstractmethod
    def labels(self) -> Collection[Label]:
        ...

    @labels.setter
    @abstractmethod
    def labels(self, labels: Collection[Label]) -> None:
        ...


class JsonStorage(SessionStorage):
    def __init__(self, source_file: str = ''):
        self.source_file: str = source_file
        self._image_path: Image = Image()
        self._labels: list[Label] = []
        self.load_source()

    @property
    def image_path(self) -> Image:
        self.load_source()
        return self._image_path

    @image_path.setter
    def image_path(self, image_path: str):
        self._image_path = image_path
        self.write_to_source()

    @property
    def labels(self) -> Collection[Label]:
        self.load_source()
        return self.labels

    @labels.setter
    def labels(self, labels: Collection[Label]) -> None:
        self._labels = labels
        self.write_to_source()

    def write_to_source(self):
        json.dump({'image_path': self._image_path, 'labels': self._labels}, open(self.source_file, 'w+'))

    def load_source(self):
        try:
            data = json.load(open(self.source_file, 'r'))
            if data:
                self.image_path = data['image_path']
                self.labels = data['labels']
        except FileNotFoundError:
            self.write_to_source()
