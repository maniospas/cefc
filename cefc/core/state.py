class State(dict):
    def __getattr__(self, key):
        try: return self[key]
        except KeyError as e: raise AttributeError(f"'DotDict' object has no attribute '{key}'") from e
    def __setattr__(self, key, value):
        self[key] = value
    def __delattr__(self, key):
        try: del self[key]
        except KeyError as e: raise AttributeError(f"'DotDict' object has no attribute '{key}'") from e
    def __repr__(self): return f"DotDict({super().__repr__()})"
