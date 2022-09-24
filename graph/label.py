import copy

from base_classes import Serializer


def near(p1, p2, threshold):
    distance = ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** .5
    return distance < threshold


class Rectangle:
    MAX_NEAR_DISTANCE = 0.05

    VERTEX_NAMES = 'top_left', 'top_right', 'bottom_left', 'bottom_right'

    def __init__(self, start_point=(0, 0), end_point=(0, 0)):
        self.hold_point = None
        self.left, self.top = start_point
        self.right, self.bottom = end_point
        self.sort()

    def __repr__(self):
        return f'{type(self).__name__}({self.top_left}, {self.bottom_right})'

    def set_vertex(self, name, position: tuple[float, float]):
        if name in self.VERTEX_NAMES:
            setattr(self, name, position)
        else:
            raise ValueError(f'Vertex name {name} is not found.')

    def move_vertex(self, name, displacement: tuple[float, float]):
        if name in self.VERTEX_NAMES:
            prev_pos = getattr(self, name)
            cur_pos = prev_pos[0] + displacement[0], prev_pos[1] + displacement[1]
            setattr(self, name, cur_pos)
        else:
            raise ValueError(f'Vertex name {name} is not found.')

    def nearby_vertex(self, point):
        for vertex_name in self.VERTEX_NAMES:
            if near(getattr(self, vertex_name), point, self.max_near_distance):
                return vertex_name

        return None

    def move(self, displacement: tuple[float, float]):
        self.move_vertex('top_left', displacement)
        self.move_vertex('bottom_right', displacement)

    @property
    def max_near_distance(self):
        return min(min(self.height, self.width) / 3, self.MAX_NEAR_DISTANCE)

    @property
    def center_x(self):
        return (self.left + self.right) / 2

    @property
    def center_y(self):
        return (self.bottom + self.top) / 2

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.top - self.bottom

    @property
    def top_left(self):
        return self.left, self.top

    @top_left.setter
    def top_left(self, position: tuple[float, float]):
        self.left, self.top = position

    @property
    def top_right(self):
        return self.right, self.top

    @top_right.setter
    def top_right(self, position: tuple[float, float]):
        self.right, self.top = position

    @property
    def bottom_left(self):
        return self.left, self.bottom

    @bottom_left.setter
    def bottom_left(self, position: tuple[float, float]):
        self.left, self.bottom = position

    @property
    def bottom_right(self):
        return self.right, self.bottom

    @bottom_right.setter
    def bottom_right(self, position: tuple[float, float]):
        self.right, self.bottom = position

    @property
    def center(self):
        return self.center_x, self.center_y

    # newly created rectangle has its left < right, and bottom < top
    def sort(self):
        self.left, self.right = sorted([self.left, self.right])
        self.bottom, self.top = sorted([self.bottom, self.top])

    def sorted(self):
        rect = copy.deepcopy(self)
        rect.sort()
        return rect

    def includes(self, point):
        sorted_rect = self.sorted()
        return sorted_rect.left <= point[0] <= sorted_rect.right and sorted_rect.bottom <= point[1] <= sorted_rect.top


class Label(Rectangle):
    def __init__(self, start=(0, 0), end=(0, 0), name='', category='', text=''):
        super().__init__(start, end)
        self.name = name
        self.category = category
        self.text = text
        self.databox: Label | None = None
        self.next = []

    def add_next(self, next_: 'Label'):
        self.next.append(next_)


class LabelSerializer(Serializer):
    def serialize(self, label: Label):
        result = {'name': label.name, 'category': label.category, 'text': label.text, 'top_left': label.top_left,
                  'bottom_right': label.bottom_right}
        if label.databox:
            result['databox'] = self.serialize(label.databox)

        return result

    def deserialize(self, label_dict):
        result = Label(
            start=label_dict['top_left'],
            end=label_dict['bottom_right'],
            name=label_dict['name'],
            category=label_dict['category'],
            text=label_dict['text']
        )

        if label_dict.get('databox'):
            result.databox = self.deserialize(label_dict['databox'])

        return result

