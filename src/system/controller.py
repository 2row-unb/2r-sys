"""
2RS Controller
"""
import logging

from .config.settings import Config
from .rxtx import Rx, Tx
from .message import Writer
from .decorators import on_message, decode_message
from .helpers import make_runner


class Controller(Rx, Writer):
    def __init__(self):
        input_topics = (
            Config.receiver.output.topic,
            Config.processor.output.topic,
        )
        super().__init__(input_topics)

        output_topics = (
            (Config.transmitter.name, Config.transmitter.input.topic),
            (Config.processor.name, Config.processor.input.topic),
        )
        self.tx = Tx(dict(output_topics))

    @on_message
    def _on_message(self, client, userdata, message):
        logging.info("[Controller] Message received")
        self.act(message)

    @decode_message(Config.receiver.name)
    def act(self, message):
        """
        Format mqtt messages
        """
        for msg in self.unzip_message(message):
            self.tx.publish(msg)
            logging.info(f'[Controller] Publishing to {msg.to}')

    def unzip_message(self, message):
        """
        Divide message data by significant parts
        """
        # [FIXME] implemente split logical
        return (
            self.write_message([1], to=Config.transmitter.name),
            self.write_message(message.data, to=Config.processor.name),
        )


run = make_runner(Controller)
