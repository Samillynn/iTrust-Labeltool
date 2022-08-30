from v2.event_listener import EventListener


class UpdateLabelListener(EventListener):
    def __init__(self):
        super().__init__()
        self.label = None

    def check(self, event, point):
        for label in self.component.labels:
            if label["coordinate"].includes(point):
                self.label = label
                return True
        return False

    def apply(self, event, values):
        event, values = UpdateLabelDialog(label)
        if event in ['Delete']:
            self.component.labels.remove(self.label)
        elif event in ['Update']:
            self.label |= values
        elif event in ['Cancel', None]:
            pass
        else:
            raise AssertionError(event)
