"""
Receiver for 2RE KERNEL module
"""
import logging

from .rxtx import Rx, Tx
from .message import Message
from .config.settings import MQTTConfig
from .decorators import on_message


def run(receiver=None):
    """
    Run an instance of receiver
    """
    if not receiver:
        receiver = Receiver()
    logging.info("Running receiver")
    receiver.run()
    return receiver


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
        logging.debug("[Receiver] received message")
        self.tx.publish(self.format(message))
        logging.debug("[Receiver] published message")

    def format(self, message):
        """
        Format mqtt messages
        """
        return Message(message.payload)
