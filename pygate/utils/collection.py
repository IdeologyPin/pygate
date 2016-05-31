class DotDict(dict):
    def __getattr__(self,attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError
