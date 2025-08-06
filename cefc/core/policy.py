class Safe:
    def __init__(self):
        self.nesting = 0
    def __commit__(self, force=False):
        raise Exception("Missing a __commit__ implementation for safe class: "+str(self.__class__))

class List(Safe):
    def __init__(self, data):
        assert isinstance(data, list)
        super().__init__()
        self.__data = data
        self.__pending = dict()
        self.__append = list()

    def __getitem__(self, key):
        return self.__pending.get(key, self.__data[key])

    def __setitem__(self, key, value):
        assert key>=0 or not self.__append, f"list cannot overwrite negative index with uncommited appended items"
        self.__pending[key] = value

    def __iter__(self):
        assert not self.__pending, "list cannot iterate over list values because at least one is modified"
        assert not self.__append, "list cannot iterate over list values because more content has been added"
        return self.__data.__iter__()

    def __len__(self):
        return len(self.__data) + len(self.__append)

    def append(self, item):
        self.__append.append(item)

    def extend(self, other):
        self.__append.extend(other)

    def __commit__(self, force=False):
        if not force:
            self.nesting -= 1
            if self.nesting: return self
        self.__data.extend(self.__append)
        for k, v in self.__pending.items(): self.__data[k] = v
        self.__pending.clear()
        self.__append.clear()
        return self.__data

def tosafe(data, policies = (List,)):
    if isinstance(data, Safe):
        data.nesting += 1
        return data
    for policy in policies:
        try: return policy(data)
        except AssertionError: pass
    return data

def fromsafe(data):
    if hasattr(data, "__commit__"): return data.__commit__()
    return data

def commit(data):
    assert hasattr(data, "__commit__"), "Cannot commit data that do not implement __commit__"
    return data.__commit__(force=True)

