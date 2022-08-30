from v2.component import Component


class GraphComponent(Component):
    def __init__(self, graph):
        self.graph = graph
        super().__init__()
        