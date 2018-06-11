"""
Decorators module
"""
from .config.settings import RPI_MOCK
from functools import wraps


def rpi_mock(alternative=lambda *a, **kw: None, *args, **kwargs):
        alternative = alternative
        alt_args = args
        alt_kwargs = kwargs

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if RPI_MOCK:
                    return alternative(*alt_args, *alt_kwargs)
                else:
                    return func(*args, **kwargs)
            return wrapper
        return decorator
