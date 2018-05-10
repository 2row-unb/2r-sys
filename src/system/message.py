"""
Module to handle message serialization
"""
import pickle


class Message:
    """
    Handler for pickle encoding data
    """
    def __new__(cls, data=None, by=None, to=None):
        if isinstance(data, bytes):
            return pickle.loads(data)

        message = object.__new__(cls)
        message.data = data
        message.by = by
        message.to = to
        return message

    encoded = property(lambda self: pickle.dumps(self))
