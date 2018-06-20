"""
2RS Controller
"""
import logging
import gabby
import time
from .state import State

class Controller(gabby.Gabby):
    """
    Class to controll all system operations and dispatch messages to
    the responsible modules
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._start_time = time.time()
        self._state = State.INITIAL
        self._power_level = 0

    def transform(self, message):
        logging.info('Controller state: ' + ('INITIAL' if self._state == State.INITIAL else 'RUNNING'))

        if self.is_message_up_to_date(message):
            if message.belongs_to('processor_controller'):
                logging.info('Received message from Processor')

                state, current_time = message.data[-2:]
                time_elapsed = int(current_time - self._start_time)

                self._state = state

                message.data = [*message.data[:-1], time_elapsed]
                message.topics = self.output_topics.filter_by(
                                    name='controller_transmitter')

                return [message]

            elif message.belongs_to('kernel_controller'):
                logging.info('Received message from Kernel')
                message.data = [*message.data[:-1], self._state, message.data[-1]]
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
        self.process_power_level(button_up, button_down)
        self.process_reset(button_reset)
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

    def process_reset(self, button_reset):
        if button_reset == 1 and self._state == State.RUNNING:
            self.reset()

    def reset(self):
        self._start_time = time.time()
        self._state = State.INITIAL # TODO: add (on) state change method
        self._power_level = 0
