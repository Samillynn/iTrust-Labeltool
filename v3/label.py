from utils import Rectangle
from v3.handler import View


class Label(Rectangle):
    def __init__(self, start=(0, 0), end=(0, 0), name: str = '', category: str = '', text: str = ''):
        super().__init__(start, end)
        self.name = name
        self.category = category
        self.text = text

    def clone(self):
        return type(self)(start=self.top_left.position, end=self.bottom_right.position, name=self.name,
                          category=self.category, text=self.text)


class LabelView(View):
    def __init__(self, label):
        super().__init__()
        self.label = label
        self.figures = []

    def _draw(self, graph):
        rect = graph.draw_rectangle(
            self.label.top_left.position, self.label.bottom_right.position,
            line_color='black',
            line_width=5)
        self.figures.append(rect)

        text = graph.draw_text(
            f'{self.label.name}\n{self.label.category}\n{self.label.text}',
            location=self.label.center_position,
            color='black', font=("Courier New Bold", 10)
        )

        self.figures.append(text)
        print('draw label', self.figures, id(self))

    def _clear(self, graph):
        print('clear label', self.figures, id(self))
        for figure in self.figures:
            graph.delete_figure(figure)
        self.figures.clear()
