import base64
import io
import time

import PIL.Image
# noinspection PyUnresolvedReferences,PyPep8Naming
import PySimpleGUI as sg


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


def get_image_size(filename):
    return PIL.Image.open(filename).size


def current_milli_time():
    return round(time.time() * 1000)


def near(p1, p2, threshold):
    distance = ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** .5
    return distance < threshold


class Rectangle:
    CENTER = 5
    TOP_LEFT = 1
    MAX_NEAR_DISTANCE = 0.05

    def __init__(self, start_point, end_point):
        self.hold_point = None
        self.left, self.top = start_point
        self.right, self.bottom = end_point
        self._reorder()

    def __repr__(self):
        return f'<Rectangle({self.top_left}, {self.bottom_right})>'

    def near(self, point):
        corners = [None, self.top_left, (self.right, self.top), (self.left, self.bottom), self.bottom_right]
        for i in range(1, 5):
            if near(corners[i], point, self.max_near_distance):
                return i
        if self.includes(point):
            return 5
        else:
            print(f'{point} not near {self}')
            return None

    def hold(self, point=None, corner_id=None):
        if corner_id is not None:
            self.hold_point = corner_id
        elif point is not None:
            self.hold_point = self.near(point)
        else:
            raise ValueError('either point or corner_id should be passed to hold.')

        return self.hold_point

    def drag(self, dx, dy):
        if self.hold_point is None:
            raise ValueError('hold should be call before drag')

        if self.hold_point == 1:
            self.left += dx
            self.top += dy
        elif self.hold_point == 2:
            self.right += dx
            self.top += dy
        elif self.hold_point == 3:
            self.left += dx
            self.bottom += dy
        elif self.hold_point == 4:
            self.right += dx
            self.bottom += dy
        elif self.hold_point == 5:
            self.left += dx
            self.right += dx
            self.top += dy
            self.bottom += dy
        else:
            raise AssertionError

    def release(self):
        self.hold_point = None
        self._reorder()

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

    @property
    def bottom_right(self):
        return self.right, self.bottom

    @property
    def center(self):
        return self.center_x, self.center_y

    def _reorder(self):
        self.left, self.right = sorted((self.left, self.right))
        self.bottom, self.top = sorted((self.bottom, self.top))

    def includes(self, point):
        return self.left <= point[0] <= self.right and self.bottom <= point[1] <= self.top


if __name__ == '__main__':
    r = Rectangle((1, 1), (2, 2))
    print(r.hold((1.5, 1.01)))
