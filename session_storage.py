import json
from typing import Collection

from base_classes import Serializer
from label import Label


class DefaultSerializer(Serializer):
    def serialize(self, obj):
        return obj

    def deserialize(self, data):
        return data


class JsonSessionStorage:
    def __init__(self, path='', label_serializer=None):
        self.path = path

        if label_serializer is None:
            label_serializer = DefaultSerializer()
        self.label_serializer = label_serializer

        self._image_path = self.image_path
        self._labels = self.labels

    @property
    def image_path(self):
        return self.read()['image_path']

    @image_path.setter
    def image_path(self, value):
        self._image_path = value
        self.write()

    @property
    def labels(self):
        serialized_labels = self.read()['labels']
        result = []
        for serialized_label in serialized_labels:
            label = self.label_serializer.deserialize(serialized_label)
            result.append(label)
            if label.databox:
                result.append(label.databox)

        return result

    @labels.setter
    def labels(self, labels: Collection[Label]):
        # nest databox into its parent label
        labels = set(labels)
        for label in labels.copy():
            if label.databox:
                labels.discard(label.databox)

        self._labels = [self.label_serializer.serialize(label) for label in labels]
        self.write()

    def read(self):
        return json.load(open(self.path, 'r'))

    def write(self):
        data = {'image_path': self._image_path, 'labels': self._labels}
        json.dump(data, open(self.path, 'w+'), indent=2)


if __name__ == '__main__':
    storage = JsonSessionStorage('test-project/session.json')
    print(storage.image_path)
    print(storage.labels)

    storage.labels = []
    print(storage.labels)

