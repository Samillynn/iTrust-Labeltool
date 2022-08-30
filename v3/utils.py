import base64
import io
import time
from math import hypot
from typing import Collection

import PIL.Image
# noinspection PyUnresolvedReferences,PyPep8Naming
import PySimpleGUI as sg


def get_image_size(filename):
    return PIL.Image.open(filename).size


def current_milli_time():
    return round(time.time() * 1000)


def convert_to_bytes(file_or_bytes, resize=None):
    '''
    Will convert into bytes and optionally resize an image that is a file or a base64 bytes object.
    Turns into  PNG format in the process so that can be displayed by tkinter
    :param file_or_bytes: either a string filename or a bytes base64 image object
    :type file_or_bytes:  (Union[str, bytes])
    :param resize:  optional new size
    :type resize: (Tuple[int, int] or None)
    :return: (bytes) a byte-string object
    :rtype: (bytes)
    '''
    if isinstance(file_or_bytes, str):
        img = PIL.Image.open(file_or_bytes)
    else:
        try:
            img = PIL.Image.open(io.BytesIO(base64.b64decode(file_or_bytes)))
        except Exception as e:
            dataBytesIO = io.BytesIO(file_or_bytes)
            img = PIL.Image.open(dataBytesIO)

    cur_width, cur_height = img.size
    if resize:
        new_width, new_height = resize
        scale = min(new_height / cur_height, new_width / cur_width)
        img = img.resize((int(cur_width * scale), int(cur_height * scale)), PIL.Image.ANTIALIAS)
    with io.BytesIO() as bio:
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()


class Vector:
    def __init__(self, x: float | int | Collection = 0, y: float | int = 0):
        if isinstance(x, Collection):
            if len(x) == 2:
                x, y = x
            else:
                raise ValueError('Length of vector should be 2')
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Vector({self.x}, {self.y})'

    def __abs__(self):
        return hypot(self.x, self.y)

    def __add__(self, other: 'Vector'):
        return self.__class__(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return self + (-other)

    def __neg__(self):
        return type(self)(-self.x, -self.y)

    def __mul__(self, scalar: float):
        return type(self)(self.x * scalar, self.y * scalar)

    def __iter__(self):
        yield self.x
        yield self.y

    def __getitem__(self, item):
        return [self.x, self.y][item]


class Vertex:
    def __init__(self, shape=None, name=None):
        self.shape = shape
        self.name = name

    def __repr__(self):
        return f'Vertex({self.shape.__class__.__name__}, {self.name})'

    @property
    def position(self) -> Vector:
        return self.shape.get_vertex_position(self.name)

    @position.setter
    def position(self, position: Vector):
        self.shape.set_vertex_position(self.name, position)


class Rectangle:
    MAX_NEAR_DISTANCE = 0.05

    def __init__(self, start: Vector = None, end: Vector = None):
        if not start:
            start = Vector()
        if not end:
            end = Vector()

        self.left, self.top = start
        self.right, self.bottom = end

    def __repr__(self):
        return f'{self.__class__.__name__}({self.top_left.position}, {self.bottom_right.position})'

    def __getattr__(self, vertex_name):
        if vertex_name in self.vertex_positions:
            return Vertex(self, vertex_name)
        else:
            raise AttributeError(f'{type(self).__name__} object has no attribute {vertex_name}')

    def set_vertex_position(self, name, position: Vector):
        match name:
            case 'top_left':
                self.left, self.top = position
            case 'top_right':
                self.right, self.top = position
            case 'bottom_left':
                self.left, self.bottom = position
            case 'bottom_right':
                self.right, self.bottom = position
            case _:
                raise ValueError(f'Vertex name {name} is not found.')

    def get_vertex_position(self, name):
        return self.vertex_positions[name]

    @property
    def vertex_positions(self) -> dict[str, Vector]:
        return {
            'top_left': Vector(self.left, self.top),
            'top_right': Vector(self.right, self.top),
            'bottom_left': Vector(self.left, self.bottom),
            'bottom_right': Vector(self.right, self.bottom)
        }

    def nearby_vertex(self, position: Vector):
        for v_name, v_pos in self.vertex_positions.items():
            if abs(v_pos - position) < self.max_near_distance:
                return Vertex(self, v_name)
        return None

    def includes(self, position: Vector):
        left, right = sorted((self.left, self.right))
        bottom, top = sorted((self.bottom, self.top))
        return left <= position.x <= right and bottom <= position.y <= top

    def move(self, displacement: Vector):
        self.top_left.position += displacement
        self.bottom_right.position += displacement

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
    def center_position(self) -> Vector:
        return Vector(self.center_x, self.center_y)

    def _reorder(self):
        self.left, self.right = sorted((self.left, self.right))
        self.bottom, self.top = sorted((self.bottom, self.top))


if __name__ == '__main__':
    r = Rectangle(Vector(1, 4), Vector(3, 2))
    top_left_v = r.nearby_vertex(Vector(1.001, 4.001))
    print(top_left_v)

    top_left_v.position = Vector(-1, 10)
    print(r.vertex_positions)
