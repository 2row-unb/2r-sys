"""
Module to filter and process all data
"""
import logging

from .config.settings import Config
from .rxtx import Rx, Tx
from .helpers import make_runner
from .message import Writer
from .decorators import decode_message, on_message


class Processor(Rx, Writer):
    def __init__(self):
        input_topics = (
           Config.processor.input.topic,
        )
        super().__init__(input_topics)

        output_topics = (
            (Config.processor.name, Config.processor.output.topic),
        )
        self.tx = Tx(dict(output_topics))

    @on_message
    def _on_message(self, client, userdata, message):
        logging.info("[Processor] Message received")
        self.act(message)

    @decode_message
    def act(self, message):
        processed_data = self.process(message.data)
        message = self.write_message(processed_data)
        logging.info("[Processor] Publishing message")
        self.tx.write(message)

    def process(self, data):
        logging.info('[Processor] processing data')
        return data


run = make_runner(Processor)
