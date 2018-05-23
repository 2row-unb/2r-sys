"""
Receiver for 2RE KERNEL module
"""
import logging

from .rxtx import Rx, Tx
from .message import Writer
from .config.settings import Config
from .decorators import on_message
from .helpers import make_runner


class Receiver(Rx, Writer):
    def __init__(self):
        topics = (Config.receiver.input.topic,)
        super().__init__(topics)

        output_topics = (
            (Config.receiver.name, Config.receiver.output.topic),
        )
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
        return self.write_message(data)


run = make_runner(Receiver)
