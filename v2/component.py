class Component:
    def __init__(self):
        self.event_listeners = []

    def add_event_listener(self, listener):
        listener.set_component(self)
        self.event_listeners.append(listener)

    def apply_event(self, event, values):
        for event_listener in self.event_listeners:
            if event_listener.check(event, values):
                event_listener.apply(event, values)
                break
