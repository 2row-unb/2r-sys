"""
Receiver for 2RE KERNEL module
"""
import logging
import gabby

from .helpers import make_runner


class Receiver(gabby.Gabby):
    """
    Class to receive messages from 2RE-Kernel and deserialize to transmit
    to 2RS-System
    """
    def transform(self, message):
        logging.info(f'Transforming data: {message.data}')
        return [gabby.Message(message.data, self.output_topics)]


run = make_runner(Receiver)
