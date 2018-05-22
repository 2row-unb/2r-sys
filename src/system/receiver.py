"""
Receiver for 2RE KERNEL module
"""
import logging

from .rxtx import Rx, Tx
from .message import FullMessage
from .config.settings import MQTTConfig
from .decorators import on_message
from .helpers import make_runner


class Receiver(Rx):
    def __init__(self):
        topics = (MQTTConfig.receiver['INPUT_TOPIC'],)
        super().__init__(topics)

        output_topics = [
            MQTTConfig.named_config('receiver','OUTPUT_TOPIC')
        ]
        self.tx = Tx(dict(output_topics))

    @on_message
    def act(self, client, userdata, message):
        logging.debug("[Receiver] Received message")
        self.tx.publish(self.format(message))
        logging.debug("[Receiver] Published message")

    def format(self, message):
        """
        Format mqtt messages
        """
        message = message.payload.decode('utf-8')
        data = map(int, message.split(';'))
        print(data)
        return FullMessage(data)


run = make_runner(Receiver)
