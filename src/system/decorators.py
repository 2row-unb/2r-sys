"""
Decorators module
"""
from functools import partial

from .message import Message


def on_message(func):
    """
    Decorator to convert a byte message to a Message object
    """
    func.ON_MESSAGE_DECORATOR = True
    return func


def on_connect(func):
    """
    Decorator to convert a byte message to a Message object
    """
    func.ON_CONNECT_DECORATOR = True
    return func
