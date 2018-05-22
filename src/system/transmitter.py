"""
Module to transmit data to 2RKernel
"""
import logging

from .rxtx import Rx, Tx
from .helpers import make_runner
from .config.settings import MQTTConfig
from .decorators import on_message, unqueued_full_message


class Transmitter(Rx):
    def __init__(self):
        topics = (MQTTConfig.transmitter['INPUT_TOPIC'],)
        super().__init__(topics)

        output_topics = (
            MQTTConfig.named_config('transmitter', 'OUTPUT_TOPIC'),
        )
        self.tx = Tx(dict(output_topics))

    @on_message
    def _on_message(self, client, userdata, message):
        logging.debug("[Transmitter] Message received")
        self.act(message)

    @unqueued_full_message
    def act(self, message):
        self.tx.write(self.serialize_data(message))
        logging.debug("[Transmitter] Published messages")

    def serialize_data(self, message):
        """
        Serialize message data to the 2RE-Kernel

        Args:
            message (Message):
                message object to be serialized
        """
        print(message.data)
        return "AAAAAAAAA"


run = make_runner(Transmitter)
