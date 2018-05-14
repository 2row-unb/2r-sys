"""
2RS Controller
"""
import pickle
import logging

from .config.settings import MQTTConfig
from .rxtx import Rx, Tx
from .message import Message
from .decorators import on_message, unqueued_message
from .helpers import make_runner

class Controller(Rx):
    def __init__(self):
        input_topics = (
            MQTTConfig.receiver['OUTPUT_TOPIC'],
            MQTTConfig.processor['OUTPUT_TOPIC'],
        )
        super().__init__(input_topics)

        output_topics = (
            MQTTConfig.named_config('transmitter', 'INPUT_TOPIC'),
        )
        self.tx = Tx(dict(output_topics))

    @on_message
    def _on_message(self, client, userdata, message):
        self.act(message)

    @unqueued_message
    def act(self, message):
        """
        Format mqtt messages
        """
        logging.debug("[Controller] Message received")
        for msg in self.unzip_message(message):
            self.tx.publish(msg)
        logging.debug("[Controller] Published messages")

    def unzip_message(self, message):
        """
        Divide message data by significant parts
        """
        #[FIXME] implemente split logical
        return (
            Message(message.data, to='processor'),
            Message(message.data, to='transmitter'),
        )


run = make_runner(Controller)
