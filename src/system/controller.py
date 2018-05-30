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
        return [gabby.Message(message.data, self.output_topics)]
