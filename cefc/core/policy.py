class Safe:
    def __init__(self):
        self._safe_nesting = 0
    def __commit__(self, force=False):
        raise Exception("Missing a __commit__ implementation for safe class: "+str(self.__class__))


class List(Safe):
    def __init__(self, data):
        assert isinstance(data, list)
        super().__init__()
        self.__data = data
        self.__pending = {}  # pending index -> new value
        self.__append = []   # list of new items to be appended (uncommitted)

    def __getitem__(self, key):
        if key in self.__pending: return self.__pending[key]
        if key >= len(self.__data): return self.__append[key - len(self.__data)]
        self.__pending[key] = tosafe(self.__data[key])
        return self.__pending[key]

    def __setitem__(self, key, value):
        assert key >= 0 or not self.__append, "list cannot overwrite negative index with uncommitted appended items"
        self.__pending[key] = tosafe(value)

    def __iter__(self):
        assert not self.__pending, "list cannot iterate with pending updates"
        assert not self.__append, "list cannot iterate with uncommitted appends"
        return iter(self.__data)

    def __len__(self):
        return len(self.__data) + len(self.__append)

    def append(self, item):
        self.__append.append(item)

    def extend(self, iterable):
        self.__append.extend(x for x in iterable)

    def __commit__(self, force=False):
        if not force:
            self._safe_nesting -= 1
            if self._safe_nesting: return self
        self.__append = [fromsafe(item) for item in self.__append]
        for k, v in self.__pending.items():
            if k < len(self.__data): self.__data[k] = fromsafe(v)
            else: self.__append[k - len(self.__data)] = fromsafe(v)
        self.__data.extend(self.__append)
        self.__pending.clear()
        self.__append.clear()
        return self.__data


class Dict(Safe):
    def __init__(self, data):
        assert isinstance(data, dict)
        super().__init__()
        self.__data = data
        self.__pending = {}  # key -> new or wrapped value
        self.__deleted = set()

    def __getitem__(self, key):
        if key in self.__deleted: raise KeyError(key)
        if key in self.__pending: return self.__pending[key]
        if key not in self.__data: raise KeyError(key)
        self.__pending[key] = tosafe(self.__data[key])
        return self.__pending[key]

    def __setitem__(self, key, value):
        if key in self.__deleted: self.__deleted.remove(key)
        self.__pending[key] = tosafe(value)

    def __delitem__(self, key):
        if key in self.__pending: del self.__pending[key]
        self.__deleted.add(key)

    def __contains__(self, key):
        if key in self.__deleted: return False
        return key in self.__pending or key in self.__data

    def __len__(self):
        return len(set(self.__data.keys()) | set(self.__pending.keys())) - len(self.__deleted)

    def __iter__(self):
        assert not self.__pending, "dict cannot iterate with pending updates"
        assert not self.__deleted, "dict cannot iterate with pending deletions"
        return iter(self.__data)

    def keys(self):
        return list(iter(self))

    def items(self):
        return [(k, self[k]) for k in self]

    def values(self):
        return [self[k] for k in self]

    def get(self, key, default=None):
        try: return self[key]
        except KeyError: return default

    def update(self, other):
        for k, v in other.items():
            self[k] = v

    def __commit__(self, force=False):
        if not force:
            self._safe_nesting -= 1
            if self._safe_nesting: return self
        for k in self.__deleted:
            if k in self.__data: del self.__data[k]
        for k, v in self.__pending.items():
            self.__data[k] = fromsafe(v)
        self.__pending.clear()
        self.__deleted.clear()
        return self.__data


class Object(Safe):
    def __init__(self, obj):
        assert not isinstance(obj, Safe), "Cannot wrap an already safe object"
        assert hasattr(obj, "__dict__"), "Object can only wrap objects with __dict__"
        super().__init__()
        self.__obj = obj
        self.__pending = {}

    def __getattr__(self, name):
        if name in self.__pending: return self.__pending[name]
        if not hasattr(self.__obj, name): raise AttributeError(name)
        self.__pending[name] = tosafe(getattr(self.__obj, name))
        return self.__pending[name]

    def __setattr__(self, name, value):
        if name.startswith("_Object__") or name == "_safe_nesting": super().__setattr__(name, value)
        else: self.__pending[name] = tosafe(value)

    def __delattr__(self, name):
        if name in self.__pending: del self.__pending[name]
        if hasattr(self.__obj, name): delattr(self.__obj, name)

    def __commit__(self, force=False):
        if not force:
            self._safe_nesting -= 1
            if self._safe_nesting: return self
        for k, v in self.__pending.items():
            setattr(self.__obj, k, fromsafe(v))
        self.__pending.clear()
        return self.__obj


def tosafe(data, policies = (List, Dict, Object, )):
    if isinstance(data, Safe):
        data._safe_nesting += 1
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

