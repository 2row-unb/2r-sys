"""
Decorators module
"""
from .message import Message


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


def decode_message(*args):
    def decode(func):
        """
        Decorator to convert a byte message to a Message object
        """
        def wrapper(self, message, *args, **kwargs):
            to = None if by else self.me
            func(self, Message(message, by=by, to=to), *args, **kwargs)
        return wrapper

    if len(args) == 1 and callable(args[0]):
        by = None
        return decode(args[0])
    else:
        by, = args
        return decode
