"""
Module to transmit data to 2RKernel
"""
import logging

from .rxtx import Rx, Tx
from .helpers import make_runner
from .message import Writer
from .config.settings import Config
from .decorators import on_message, decode_message


class Transmitter(Rx, Writer):
    def __init__(self):
        topics = (Config.transmitter.input.topic,)
        super().__init__(topics)

        output_topics = (
            (Config.kernel.name, Config.kernel.input.topic),
        )
        self.tx = Tx(dict(output_topics))

    @on_message
    def _on_message(self, client, userdata, message):
        logging.info("[Transmitter] Message received")
        self.act(message)

    @decode_message
    def act(self, message):
        serialized_data = self.serialize_data(message.data)
        msg = self.write_message(serialized_data, to=Config.kernel.name)
        logging.info(f"[Transmitter] Publishing to {msg.to}")
        self.tx.publish(msg)

    def serialize_data(self, data):
        """
        Serialize message data to the 2RE-Kernel

        Args:
            message (Message):
                message object to be serialized
        """
        return data


run = make_runner(Transmitter)
