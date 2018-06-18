"""
Class to handle buttons end measures made by kernel
"""
import gabby
import logging
import time
import random
import _thread

from .decorators import rpi_mock
from .config.settings import RPI_MOCK

try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    assert RPI_MOCK is True
else:
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)


class KernelControl(gabby.Gabby):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.power_level = 0
        self._setup_relays(37, 35, 33, 31)
        self._setup_buttons(up=18, down=11, reset=12)

    def transform(self, client, message):
        if message.belongs_to('controller_kernelcontrol'):
            self.update_power_level(message.data)
        return []

    def run(self):
        _thread.start_new_thread(self.exec_buttons_reader, tuple())
        super().run()

    @rpi_mock()
    def _turn(self, pins, state):
        if isinstance(pins, list):
            for i in pins:
                GPIO.output(i, state)
        else:
            GPIO.output(pins, state)

    def update_power_level(self, button_data):
        _ON = 0
        _OFF = 1
        power_level, = button_data

        logging.warning(f'Changing power level to {power_level}')

        self._turn(self.RELAYS_PINS, _OFF)
        if power_level >= 0 and power_level < 4:
            self._turn(self.RELAYS_PINS[power_level], _ON)

    def exec_buttons_reader(self):
        for new_state in self.get_buttons():
            self.send(
                gabby.Message(
                    new_state,
                    self.output_topics.filter_by(
                        name='kernelcontrol_controller'
                    )
                )
            )

    def get_buttons(self):
        while(True):
            states = [self._read_button(b) for _, b in self.BUTTONS.items()]
            if any(states):
                yield states
                time.sleep(0.6)
            else:
                time.sleep(0.1)

    @rpi_mock(lambda: random.randint(0, 1))
    def _read_button(self, button):
        return GPIO.input(button)

    def _setup_buttons(self, **buttons):
        self.BUTTONS = buttons
        for _, pin in buttons.items():
            self._setup_pin(pin, 'input')

    def _setup_relays(self, *pins):
        self.RELAYS_PINS = pins
        for pin in self.RELAYS_PINS:
            self._setup_pin(pin, 'output')

    @rpi_mock()
    def _setup_pin(self, pin, state):
        if state == 'input':
            GPIO.setup(pin, GPIO.IN)
        elif state == 'output':
            GPIO.setup(pin, GPIO.OUT)
        else:
            raise AttributeError
