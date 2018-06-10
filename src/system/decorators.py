"""
Decorators module
"""
from .config.settings import RPI_MOCK
from functools import wraps


class rpi_mock:
    def __init__(self, alternative_return):
        self.return_ = alternative_return

    def __call__(self, func, *args, **kwargs):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if RPI_MOCK:
                return self.return_
            else:
                return func(*args, **kwargs)
        return wrapper
