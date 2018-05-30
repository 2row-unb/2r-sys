"""
Receiver for 2RE KERNEL module
"""
import logging
import gabby


class Receiver(gabby.Gabby):
    """
    Class to receive messages from 2RE-Kernel and deserialize to transmit
    to 2RS-System
    """
    def transform(self, message):
        logging.info(f'Transforming data: {message.payload.decode("utf-8")}')
        decoded_data = [float(x) for x in
                        message.payload.decode('utf-8').split(';')]
        return [gabby.Message(decoded_data, self.output_topics)]
