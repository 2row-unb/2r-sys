"""
2RS Controller
"""
import logging
import gabby


class Controller(gabby.Gabby):
    """
    Class to controll all system operations and dispatch messages to
    the responsible modules
    """
    def transform(self, message):
        logging.info(f'Transforming data {message.data}')

        if message.belongs_to('processor_controller'):
            logging.info('Received message from processor')
            message.topics = self.output_topics.filter_by(
                name='controller_transmitter'
            )
            return [message]

        elif message.belongs_to('kernel_controller'):
            logging.info('Received message from receiver')
            return [
                gabby.Message(
                    message.data[:18],
                    topics=(
                        self
                        .output_topics
                        .filter_by(name='controller_processor')
                    )
                ),
            ]

        return []
