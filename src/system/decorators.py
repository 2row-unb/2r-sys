"""
Decorators module
"""
from .config.settings import RPI_MOCK
from functools import wraps


class rpi_mock:
    def __init__(self, alternative=lambda *a, **kw: None, *args, **kwargs):
        self.alternative = alternative
        self.args = args
        self.kwargs = kwargs

    def __call__(self, func, *args, **kwargs):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if RPI_MOCK:
                return self.alternative(*self.args, *self.kwargs)
            else:
                return func(*args, **kwargs)
        return wrapper
