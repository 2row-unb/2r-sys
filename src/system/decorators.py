"""
Decorators module
"""
from config.settings import RPI_MOCK


def rpi_mock(alternative_return):
    def _(func):
        return func
    return _
