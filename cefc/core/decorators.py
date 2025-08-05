import inspect
from functools import wraps
from cefc.core.state import State
from cefc.core.policy import tosafe, fromsafe

class ansi:
    red = "\033[91m"
    yellow = "\033[93m"
    blue = "\033[94m"
    reset = "\033[0m"

class SafeException(Exception):
    # NEVER add a __commit__ method to this
    def __init__(self, description: str, frames: list[str]):
        self.frames = frames
        self.description = description
        self.handled = False
        super().__init__(f"{description}\n{ansi.blue}->{ansi.reset} "+f"\n{ansi.blue}->{ansi.reset} ".join(frames))
    def __del__(self):
        if not self.handled:
            print(f"{ansi.red}Unhandled error:{ansi.reset} {self}")
    def __bool__(self):
        self.handled = True
        return False
    @property
    def value(self):
        return self

class Monad:
    # NEVER add a __commit__ method to this
    def __init__(self, value: any):
        self.__value = value
    def __bool__(self):
        return False
    @property
    def value(self):
        return self.__value

def funcdesc(f):
    return f"{f.__name__}\n   {inspect.getfile(f)}:{inspect.getsourcelines(f)[1]}"

def service(f, name: str|None=None, state: State|None=None):
    @wraps(f)
    def decorator(*args, **kwargs):
        for e in args:
            if isinstance(e, SafeException):
                bool(e)
                return SafeException(e.description, e.frames+[name if name else funcdesc(f)])
        for e in kwargs.values():
            if isinstance(e, SafeException):
                bool(e)
                return SafeException(e.description, e.frames+[name if name else funcdesc(f)])
        args = [tosafe(v) for v in args]
        kwargs = {k: tosafe(v) for k, v in kwargs.items()}
        try:
            if state is not None: result = f(*args, state=state, **kwargs)
            else: result = f(*args, **kwargs)
            if isinstance(result, SafeException):
                e = result
                bool(e)
                result = SafeException(e.description, e.frames + [name if name else funcdesc(f)])
        except SafeException as e:
            bool(e)
            result = SafeException(e.description, e.frames+[name if name else funcdesc(f)])
        except Exception as e:
            result = SafeException(str(e), [name if name else funcdesc(f)])
        return fromsafe(result)
    return decorator
