"""
2RS Controller
"""
import logging
import gabby
import time


class Controller(gabby.Gabby):
    """
    Class to controll all system operations and dispatch messages to
    the responsible modules
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._power_level = 0

    def transform(self, message):
        if self.is_message_up_to_date(message):
            if message.belongs_to('processor_controller'):
                logging.info('Received message from Processor')
                message.topics = self.output_topics.filter_by(
                    name='controller_transmitter'
                )
                return [message]

            elif message.belongs_to('kernel_controller'):
                logging.info('Received message from Kernel')
                return [
                    *self.process_views(
                        [*message.data[:19], message.data[-1]]),
                    *self.process_buttons(message.data[19:22]),
                ]

        return []

    def is_message_up_to_date(self, message):
        current_time = time.time()
        time_delta = current_time - message.data[-1]
        logging.debug(
            f'Time msg: {message.data[-1]} | '
            f'Time now: {current_time} | '
            f'Time delta: {time_delta}'
        )
        return time_delta < 0.04  # 25 frames per second

    def process_views(self, data):
        return [
            gabby.Message(
                data,
                topics=(
                    self
                    .output_topics
                    .filter_by(
                        name='controller_processor'
                    )
                )
            )
        ]

    def process_buttons(self, buttons):
        old_power_level = self._power_level
        new_power_level = self.process_power_level(*buttons[:2])
        if old_power_level != new_power_level:
            return [
                gabby.Message(
                    (new_power_level,),
                    topics=(
                        self
                        .output_topics
                        .filter_by(
                            name='controller_kernel'
                        )
                    )
                )
            ]
        else:
            return []

    def process_power_level(self, button_up, button_down):
        power_level = self._power_level
        power_level += button_up - button_down
        self._power_level = power_level % 4 if power_level >= 0 else 0
        return self._power_level
