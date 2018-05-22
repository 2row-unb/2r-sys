"""
Module to handle message serialization
"""
import struct
from paho.mqtt.client import MQTTMessage

from .config.settings import MQTTConfig

class Message:
    """
    Handler for pickle encoding data
    """
    _fmt = None

    def __new__(cls, data=None, by=None, to=None):
        if isinstance(data, MQTTMessage):
            by, to, *data = struct.unpack(cls._fmt, data.payload)
            by = MQTTConfig.find_code(by) if by > 0 else None
            to = MQTTConfig.find_code(to) if to > 0 else None

        message = object.__new__(cls)
        message.data = data
        message.by = by
        message.to = to
        return message

    @property
    def encoded(self):
        return struct.pack(
            self.__class__._fmt,
            MQTTConfig.named_config(self.by, 'CODE')[1] if self.by else -1,
            MQTTConfig.named_config(self.to, 'CODE')[1] if self.to else -1,
            *self.data
        )


class ActionMessage(Message):
    _fmt = "i"*3


class FullMessage(Message):
    """
    (accelx1, accely1, accelz1, girox1, giroy1, giroz1, magnx1,
    magny1, magnz1, accelx2, accely2, accelz2, girox2, giroy2,
    giroz2, magnx2, magny2, magnz2, pot, temp,
    button1, button2 , button3)
    """
    _fmt = "i"*25
