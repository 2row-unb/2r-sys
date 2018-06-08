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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._power_level = 0

    def transform(self, message):
        logging.info(f'Transforming data {message.data}')

        if message.belongs_to('processor_controller'):
            logging.info('Received message from Processor')
            message.topics = self.output_topics.filter_by(
                name='controller_transmitter'
            )
            return [message]

        elif message.belongs_to('kernel_controller'):
            logging.info('Received message from Kernel')
            return [
                self.process_views(message.data[:20]),
                self.process_buttons(message.data[:13]),
            ]

        return []

    def process_views(self, data):
        return gabby.Message(
            data,
            topics=(
                self.output_topics
                .filter_by(name='controller_processor')
            )
        )

    def process_buttons(self, buttons):
        new_power_level = self.process_power_level(*buttons[:2])
        return gabby.Message(
            (new_power_level,),
            topics=(
                self.output_topics
                .filter_by(name='controller_kernel')
            )
        )

    def process_power_level(self, button_up, button_down):
        if button_up and self._power_level < 4:
            self._power_level += 1
        elif button_down and self._power_level > 0:
            self._power_level -= 1
        return self._power_level
