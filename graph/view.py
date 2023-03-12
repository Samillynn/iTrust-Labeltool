import itertools
from abc import ABC, abstractmethod
from typing import Iterable
from .label import LabelType

import globl
from config import config
from graph.image import Image
from graph.label import Label


class View(ABC):
    def __init__(self, graph):
        self.graph = graph
        self._enabled = True
        self.figure_ids = []

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, val):
        if val is True:
            self._enabled = True
            self.draw()
        elif val is False:
            self.clear()
            self._enabled = False
        else:
            raise ValueError(f"{self.__class__.__name__}.enabled can only be True or False, not {val}.")

    def draw(self):
        self.clear()

        if self.enabled:
            self.figure_ids = list(self._draw())
        else:
            # do nothing
            ...

    def clear(self):
        for fid in self.figure_ids:
            self.graph.delete_figure(fid)

    @abstractmethod
    def _draw(self) -> Iterable[int]:
        ...


class AbstractLabelView(View, ABC):
    def __init__(self, graph):
        super().__init__(graph)
        self._labels = []

    @property
    def labels(self):
        return self._labels

    @labels.setter
    def labels(self, val):
        self._labels = val
        self.draw()

    def _draw(self) -> Iterable[int]:
        return list(itertools.chain.from_iterable(self.draw_one(label) for label in self.labels))

    @abstractmethod
    def draw_one(self, label) -> Iterable[int]:
        ...


class RectangleView(AbstractLabelView):
    def draw_one(self, label) -> list[int]:
        # method 3: change border color
        color = ""
        if label.type == LabelType.COMPONENT:
            color = "#cb21d1"
        elif label.type == LabelType.DATABOX:
            color = "#d1c821"
        else:
            color = "#0b36d4"
        if label.selected:
            color = "#34eb67"
        return [self.graph.draw_rectangle(label.top_left, label.bottom_right, line_color=color, line_width=3)]


class LabelTextView(AbstractLabelView):
    def draw_one(self, label) -> list[int]:
        font = config["display"]["font"]
        text = font["format"].format(**label.basic_properties)
        color = font["color"]
        type_ = font["type"]
        size = font["size"]
        
        
        # method 1: use text
        prefix = ""
        if label.type == LabelType.COMPONENT:
            prefix = "component"
        else:
            prefix = "databox"
            
        fulltext = ""
        if text != "":
            fulltext = text+" "+prefix
            
        # method 2: use short name
        prefix = ""
        if label.type == LabelType.COMPONENT:
            prefix = "C"
        elif label.type == LabelType.DATABOX:
            prefix = "D"
        else:
            prefix = "B"
            
        fulltext = ""
        if text != "":
            fulltext = text+" "+prefix
        

        return [self.graph.draw_text(fulltext, location=label.center, color=color, font=(type_, size))]


class ConnectionView(AbstractLabelView):
    def draw_one(self, label) -> list[int]:
        return [self.graph.draw_line(label.center, conn.center)
                for conn in label.connections]


class ImageView(View):
    def __init__(self, graph):
        super().__init__(graph)
        self._image = Image()

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, image: Image):
        self._image = image
        self.draw()

    def _draw(self) -> Iterable[int]:
        self.graph.set_size(self.image.size)
        return [self.graph.draw_image(data=self.image.data, location=(-1, 1))]


class GraphView2:
    def __init__(self, graph):
        self.graph = graph
        self._image: Image = Image()
        self._labels: list[Label] = []

        self.label_views = [
            RectangleView(self.graph),
            LabelTextView(self.graph),
            ConnectionView(self.graph),
        ]
        globl.connection_view = self.label_views[2]

        self.image_view = ImageView(self.graph)

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, image: Image):
        self._image = image
        self.image_view.image = image

        # assign self.labels to render labels again
        # otherwise image will hide all labels
        self.labels = self.labels

    @property
    def labels(self):
        return self._labels

    @labels.setter
    def labels(self, labels: list[Label]):
        self._labels = labels
        for view in self.label_views:
            view.labels = labels
