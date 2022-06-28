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


class Coordinate:
    def __init__(self, start_point, end_point):
        self.left, self.right = sorted((start_point[0], end_point[0]))
        self.bottom, self.top = sorted((start_point[1], end_point[1]))
        self.center_x = (self.left + self.right) / 2
        self.center_y = (self.bottom + self.top) / 2
        self.width = self.right - self.left
        self.height = self.top - self.bottom
        self.top_left = (self.left, self.top)
        self.bottom_right = (self.right, self.bottom)
        self.center = (self.center_x, self.center_y)

    def is_surrounding(self, point):
        return self.left <= point[0] <= self.right and self.bottom <= point[1] <= self.top
