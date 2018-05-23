"""
Module to handle message serialization
"""
import struct
import logging
from paho.mqtt.client import MQTTMessage

from .config.settings import Config


class Message:
    """
    Handler for struct encoding data
    """
    def __new__(cls, data, by=None, to=None):
        fmt = (getattr(Config, to).input.fmt if to
               else getattr(Config, by).output.fmt)

        if isinstance(data, MQTTMessage):
            logging.debug("Converting MQTTMessage to Message Object")
            logging.debug(f"Using format: {fmt}")
            data = struct.unpack(fmt, data.payload)

        logging.debug(f'New message data: {data}')
        message = object.__new__(cls)
        message.data = data
        message.by = by
        message.to = to
        message.fmt = fmt
        return message

    @property
    def encoded(self):
        return struct.pack(self.fmt, *self.data)

    def __str__(self):
        return str(self.data)


class Writer:
    @property
    def me(self):
        return self.__class__.__name__.lower()

    def write_message(self, data, to=None):
        return Message(data, to=to, by=self.me)
