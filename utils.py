class Factory:
    def __init__(self):
        self._builders = {}

    def register(self, func, name=None):
        self._builders[name or func.__name__] = func
        return func

    def __getitem__(self, key):
        try:
            return self._builders.__getitem__(key)
        except KeyError:
            raise NotImplementedError(f"function {key} is not yet implemented")
