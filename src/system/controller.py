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

        if message.topics.name == '2rs/processor/output':
            logging.info(f'Sending to viewer {message.data}')
            # return [gabby.Message(message.data, list(filter(lambda x : x.name == '2rs/viewer/input', self.output_topics)))]
            return []

        return [gabby.Message(message.data, self.output_topics)]