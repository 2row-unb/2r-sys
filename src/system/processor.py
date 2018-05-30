"""
Module to filter and process all data
"""
import logging
import gabby

from .helpers import make_runner


class Processor(gabby.Gabby):
    """
    Class to process IMU data comming from 2RE-Suit
    """
    def transform(self, message):
        logging.info(f'Transforming data: {message.data}')
        return [gabby.Message(message.data, self.output_data)]


run = make_runner(Processor)
