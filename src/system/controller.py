"""
2RS Controller
"""
import logging

from .config.settings import MQTTConfig
from .rxtx import Rx, Tx
from .message import FullMessage
from .decorators import on_message, unqueued_full_message
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
        logging.debug("[Controller] Message received")
        self.act(message)

    @unqueued_full_message
    def act(self, message):
        """
        Format mqtt messages
        """
        for msg in self.unzip_message(message):
            self.tx.publish(msg)
        logging.debug("[Controller] Published messages")

    def unzip_message(self, message):
        """
        Divide message data by significant parts
        """
        #[FIXME] implemente split logical
        return (
            FullMessage(message.data, to='processor'),
            FullMessage(message.data, to='transmitter'),
        )


run = make_runner(Controller)
