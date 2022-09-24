import base64
import io

import PIL.Image
import cv2


class CoordinateTransfer:
    def __init__(self, relative_bottom_left, relative_top_right, absolute_size):
        self.absolute_size = absolute_size
        self.bottom_left = relative_bottom_left
        self.top_right = relative_top_right

    def to_absolute(self, relative_position: tuple[float, float]):
        x_in, y_in = relative_position

        scale_x = (self.absolute_size[0] - 0) / (self.top_right[0] - self.bottom_left[0])
        scale_y = (0 - self.absolute_size[1]) / (self.top_right[1] - self.bottom_left[1])

        x_out = 0 + (x_in - self.bottom_left[0]) * scale_x
        y_out = self.absolute_size[1] + (y_in - self.bottom_left[1]) * scale_y

        return int(x_out), int(y_out)

    def to_relative(self, absolute_position: tuple[int, int]):
        x_in, y_in = absolute_position

        scale_x = (self.absolute_size[0] - 0) / (self.top_right[0] - self.bottom_left[0])
        scale_y = (0 - self.absolute_size[1]) / (self.top_right[1] - self.bottom_left[1])

        x_out = x_in / scale_x + self.bottom_left[0]
        y_out = (y_in - self.absolute_size[1]) / scale_y + self.bottom_left[1]

        return x_out, y_out


class Image:
    def __init__(self, path: str = ''):
        self.path: str = path
        self._resize: float = 1

    def __repr__(self):
        return f'{type(self).__name__}({self.path})'

    def to_nparray(self):
        return cv2.imread(self.path)

    @property
    def data(self) -> bytes:
        if self.path:
            return convert_to_bytes(self.path, self.size)
        else:
            return b''

    @property
    def resize(self):
        return self._resize

    @resize.setter
    def resize(self, value):
        if value < 0:
            raise ValueError(f'Resize ratio should be positive: {value}')
        else:
            self._resize = value

    @property
    def size(self) -> tuple[int, int]:
        width, height = get_image_size(self.path)
        return int(width * self.resize), int(height * self.resize)


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