"""
Transmitter for 2RE KERNEL module
"""
import logging
import gabby

from .helpers import make_runner


class Transmitter(gabby.Gabby):
    """
    Class to receive messages from 2RS-Controller and serialize to transmit
    to 2RE-Kernel
    """
    def transform(self, message):
        logging.info(f'Transforming data: {message.data}')
        return [gabby.Message(message.data, self.output_topics)]


run = make_runner(Transmitter)
