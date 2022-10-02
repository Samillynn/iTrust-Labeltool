import copy
from typing import Collection

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
    max_instance_id = 0

    def __init__(self, start=(0, 0), end=(0, 0), name='', category='', flip=0, rotation=0.0, parent='', fullname='', id_=None):
        # advanced properties
        super().__init__(start, end)

        if isinstance(id_, int):
            self.id = id_
            self.max_instance_id = max(self.max_instance_id, id_)
        else:
            self.max_instance_id += 1
            self.id = self.max_instance_id

        self.databox: Label | None = None
        self.next = []

        # basic properties
        self.name = name
        self.flip = flip
        self.rotation = rotation
        self.category = category
        self.parent = parent
        self.fullname = fullname

        self.connections = []

    def add_connection(self, label: 'Label'):
        self.connections.append(label)

    def remove_connections(self, label: 'Label'):
        self.connections.remove(label)

    def copy_basic_properties(self, label_dict):
        self.name = label_dict.get('name', '')
        self.category = label_dict.get('category', '')
        self.fullname = label_dict.get('fullname', '')
        self.parent = label_dict.get('parent', '')
        self.flip = label_dict.get('flip', 0)
        self.rotation = label_dict.get('rotation', 0)


class LabelSerializer(Serializer):
    def serialize(self, label: Label) -> dict:
        result = {'name': label.name, 'category': label.category, 'flip': label.flip, 'rotation': label.rotation,
                  'parent': label.parent, 'fullname': label.fullname, 'top_left': label.top_left,
                  'bottom_right': label.bottom_right}

        # save databox
        if label.databox:
            result['databox'] = self.serialize(label.databox)

        # save connections
        result['connections'] = [self.serialize(conn) for conn in label.connections]

        return result

    def deserialize(self, label_dict: dict) -> Label:
        result = Label(
            start=label_dict.get('top_left', None),
            end=label_dict.get('bottom_right', None),
            id_=label_dict.get('id_')
        )
        result.copy_basic_properties(label_dict)

        if label_dict.get('databox'):
            result.databox = self.deserialize(label_dict['databox'])

        for conn_dict in label_dict['connections']:
            print('connected', conn_dict)
            result.add_connection(self.deserialize(conn_dict))

        return result


class LabelListSerializer:
    def __init__(self, label_serializer=None):
        if label_serializer is None:
            label_serializer = LabelSerializer()

        self.label_serializer = label_serializer

    def serialize(self, labels: Collection[Label]) -> list[dict]:
        labels = set(labels)
        for label in labels.copy():
            if label.databox:
                labels.discard(label.databox)
            for conn in label.connections:
                labels.discard(conn)

        return [self.label_serializer.serialize(label) for label in labels]

    def deserialize(self, label_dicts: Collection[dict]) -> list[Label]:
        result = []
        for label_dict in label_dicts:
            label = self.label_serializer.deserialize(label_dict)
            result.append(label)
            if label.databox:
                result.append(label.databox)
            for conn in label.connections:
                result.append(conn)

        return result
