from handler import Filter, FilteredHandler


class KeyFilter(Filter):
    def __init__(self, key: str):
        self.key = key

    def filter(self, e):
        if not e.name.startswith(self.key):
            return None

        e.name.removeprefix(self.key)
        if isinstance(e.value, dict):
            e.value = e.value[self.key]
        return e


def KeyHandler(key, handler):
    return FilteredHandler(KeyFilter(key), handler)
