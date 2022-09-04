from v2.base_classes import Serializer
from v2.utils import Rectangle


class Label(Rectangle):
    def __init__(self, start=(0, 0), end=(0, 0), name='', category='', text=''):
        super().__init__(start, end)
        self.name = name
        self.category = category
        self.text = text


class LabelSerializer(Serializer):
    def serialize(self, label: Label):
        return {'name': label.name, 'category': label.category, 'text': label.text, 'top_left': label.top_left,
                'bottom_right': label.bottom_right}

    def deserialize(self, label_dict):
        return Label(
            start=label_dict['top_left'],
            end=label_dict['bottom_right'],
            name=label_dict['name'],
            category=label_dict['category'],
            text=label_dict['text']
        )
