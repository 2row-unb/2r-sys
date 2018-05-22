"""
Decorators module
"""
from .message import FullMessage


def on_message(func):
    """
    Decorator to configure MQTT paho on_message by RxMeta
    """
    func.ON_MESSAGE_DECORATOR = True
    return func


def on_connect(func):
    """
    Decorator to configure MQTT paho on_connect by RxMeta
    """
    func.ON_CONNECT_DECORATOR = True
    return func


def unqueued_full_message(func):
    """
    Decorator to convert a byte message to a Message object
    """
    def wrapper(self, message, *args, **kwargs):
        func(self, FullMessage(message), *args, **kwargs)
    return wrapper
