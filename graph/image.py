import base64
import io

import PIL.Image
import PIL.ImageEnhance
import cv2

from graph.label import Rectangle


class CoordinateTransfer:
    def __init__(self, relative_bottom_left, relative_top_right, absolute_size):
        self.absolute_size = absolute_size
        self.bottom_left = relative_bottom_left
        self.top_right = relative_top_right

    def to_absolute(self, relative_position: tuple[float, float]):
        x_in, y_in = relative_position

        scale_x = (self.absolute_size[0] - 0) / \
            (self.top_right[0] - self.bottom_left[0])
        scale_y = (0 - self.absolute_size[1]) / \
            (self.top_right[1] - self.bottom_left[1])

        x_out = 0 + (x_in - self.bottom_left[0]) * scale_x
        y_out = self.absolute_size[1] + (y_in - self.bottom_left[1]) * scale_y

        return int(x_out), int(y_out)

    def to_relative(self, absolute_position: tuple[int, int]):
        x_in, y_in = absolute_position

        scale_x = (self.absolute_size[0] - 0) / \
            (self.top_right[0] - self.bottom_left[0])
        scale_y = (0 - self.absolute_size[1]) / \
            (self.top_right[1] - self.bottom_left[1])

        x_out = x_in / scale_x + self.bottom_left[0]
        y_out = (y_in - self.absolute_size[1]) / scale_y + self.bottom_left[1]

        return x_out, y_out

    def rect_to_absolute(self, rect: Rectangle) -> Rectangle:
        return Rectangle(self.to_absolute(rect.top_left), self.to_absolute(rect.bottom_right))

    def rect_to_relative(self, rect: Rectangle) -> Rectangle:
        return Rectangle(self.to_relative(rect.top_left), self.to_relative(rect.bottom_right))


class Image:
    def __init__(self, path: str = ''):
        self.path: str = path
        self._resize: float = 1
        self.shadow = False

    def __repr__(self):
        return f'{type(self).__name__}({self.path})'

    def to_nparray(self):
        return cv2.imread(self.path)

    def crop(self, rect: Rectangle, coord=None):
        if coord is None:
            coord = CoordinateTransfer(relative_bottom_left=(-1, -1), relative_top_right=(1, 1),
                                       absolute_size=self.original_size)

        absolute_rect = coord.rect_to_absolute(rect)
        left, top = absolute_rect.top_left
        right, bottom = absolute_rect.bottom_right
        return self.to_nparray()[bottom:top + 1, left:right + 1]

    def crop_for_ocr(self, rect: Rectangle, coord=None):
        if coord is None:
            coord = CoordinateTransfer(relative_bottom_left=(-1, -1), relative_top_right=(1, 1),
                                       absolute_size=self.original_size)

        absolute_rect = coord.rect_to_absolute(rect)
        left, top = absolute_rect.top_left
        right, bottom = absolute_rect.bottom_right
        print(bottom, right)
        return self.to_nparray()[bottom-20:top + 41, left-20:right + 21]

    @property
    def data(self) -> bytes:
        if self.path:
            return convert_to_bytes(self.path, self.size, self.shadow)
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
            
    def add_shadow(self):
        self.shadow = True
        
    def remove_shadow(self):
        self.shadow = False

    @property
    def size(self) -> tuple[int, int]:
        width, height = get_image_size(self.path)
        return int(width * self.resize), int(height * self.resize)

    @property
    def original_size(self) -> tuple[int, int]:
        return get_image_size(self.path)


def convert_to_bytes(file_or_bytes, resize=None, shadow=False):
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
        dpi = img.info["dpi"]
        if dpi[0] < 290:
            img.save(file_or_bytes,"PNG",dpi=(300,300))
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
        img = img.resize(
            (int(cur_width * scale), int(cur_height * scale)), PIL.Image.ANTIALIAS)
    
    if shadow:
        img = PIL.ImageEnhance.Brightness(img).enhance(0.5)
    with io.BytesIO() as bio:
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()


def get_image_size(filename):
    return PIL.Image.open(filename).size
