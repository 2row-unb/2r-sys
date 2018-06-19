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
        self._start_time = time.time()
        self._state = 1
        self._power_level = 0

    def transform(self, message):
        if self.is_message_up_to_date(message):
            if message.belongs_to('processor_controller'):
                logging.info('Received message from Processor')
                message.topics = self.output_topics.filter_by(
                                    name='controller_transmitter')
                return [message]

            elif message.belongs_to('kernel_controller'):
                logging.info('Received message from Kernel')
                return self.process_views(message.data)

        if message.belongs_to('kernelcontrol_controller'):
            logging.info('Received message from Kernel Control')
            return self.process_buttons(message.data)

        return []

    def is_message_up_to_date(self, message):
        current_time = time.time()
        time_delta = current_time - message.data[-1]
        logging.debug(
            f'Time msg: {message.data[-1]} | '
            f'Time now: {current_time} | '
            f'Time delta: {time_delta}'
        )
        return time_delta < 0.05  # 20 frames per second

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
        button_up, button_down, button_reset = buttons
        old_power_level = self._power_level
        if button_reset == 1:
            self.reset()
        else:
            self.process_power_level(button_up, button_down)
        new_power_level = self._power_level
        if old_power_level != new_power_level:
            return [
                gabby.Message(
                    (new_power_level,),
                    topics=(
                        self
                        .output_topics
                        .filter_by(
                            name='controller_kernelcontrol'
                        )
                    )
                )
            ]
        else:
            return []

    def process_power_level(self, button_up, button_down):
        power_level = self._power_level
        power_level += button_up - button_down
        if power_level > 3:
            power_level = 3
        elif power_level < 0:
            power_level = 0
        self._power_level = power_level
        logging.debug(f'Button UP: {button_up} | '
                      f'Button DOWN: {button_down} | '
                      f'Current power level: {self._power_level}')
        return self._power_level

    def reset(self):
        self._start_time = time.time()
        self._state = 1 # TODO: add (on) state change method
        self._power_level = 0