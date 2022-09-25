import json
from typing import Collection

from graph.label import Label, LabelSerializer, LabelListSerializer


class JsonSessionStorage:
    def __init__(self, path, label_list_serializer=None):
        self.path = path

        if label_list_serializer is None:
            label_list_serializer = LabelListSerializer()
        self.label_list_serializer = label_list_serializer

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
        return self.label_list_serializer.deserialize(serialized_labels)

    @labels.setter
    def labels(self, labels: Collection[Label]):
        self._labels = self.label_list_serializer.serialize(labels)
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
