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

_ON = 0
_OFF = 1


class KernelControl(gabby.Gabby):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.power_level = 0

    def transform(self, client, message):
        if message.belongs_to('controller_kernelcontrol'):
            self.update_power_level(message.data)

    def run(self):
        self._setup_relays(37, 35, 33, 31)
        self._setup_buttons(up=18, down=11, reset=12)
        _thread.start_new_thread(self.exec_buttons_reader, tuple())
        _thread.start_new_thread(self.update_force_measure, tuple())
        super().run()

    @rpi_mock()
    def _turn(self, pins, state):
        if isinstance(pins, list):
            for i in pins:
                GPIO.output(i, state)
        else:
            GPIO.output(pins, state)

    def update_power_level(self, button_data=(0,)):
        power_level, = button_data

        logging.warning(f'Changing power level to {power_level}')

        self._turn(self.RELAYS_PINS, _OFF)
        if power_level >= 0 and power_level < 4:
            self._turn(self.RELAYS_PINS[power_level], _ON)
        else:
            logging.error(f'Invalid power level value {power_level}')
            logging.error('Setting relay_pins to zero')
            self._turn(self.RELAYS_PINS[0], _ON)

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
        self.update_power_level()

    @rpi_mock()
    def _setup_pin(self, pin, state):
        if state == 'input':
            GPIO.setup(pin, GPIO.IN, GPIO.PUD_DOWN)
        elif state == 'output':
            GPIO.setup(pin, GPIO.OUT)
        else:
            raise AttributeError

    def update_force_measure(self):
        for new_force_measure in self.get_force_measure():
            self.send(
                gabby.Message(
                    (new_force_measure,),
                    self.output_topics.filter_by(
                        name='kernelcontrol_kernel'
                    )
                )
            )

    def get_force_measure(self):
        DAT1 = 15
        CLK1 = 16
        DAT2 = 13
        CLK2 = 8

        while True:
            strain_gages = ((DAT1, CLK1, 6020), (DAT2, CLK2, 5943))
            total_weight = sum(
                [self._get_normalized_weight(dat, clk, offset)
                 for dat, clk, offset in strain_gages]
            )
            power = total_weight*9.81*0.7071

            yield power if power > 0 else 0
            time.sleep(0.3)

    @rpi_mock(lambda: random.random() * 80)
    def _get_normalized_weight(self, dat, clk, offset):
        counter = 0
        GPIO.setup(clk, GPIO.OUT)
        GPIO.setup(dat, GPIO.OUT)
        GPIO.output(dat, 1)
        GPIO.output(clk, 0)
        GPIO.setup(dat, GPIO.IN)

        while GPIO.input(dat):
            pass

        for _ in range(24):
            GPIO.output(clk, 1)
            counter = counter << 1

            GPIO.output(clk, 0)
            if GPIO.input(dat) == 0:
                counter += 1

        GPIO.output(clk, 1)
        counter ^= 0x800000
        GPIO.output(clk, 0)
        weight = ((counter)/1406)
        normalized_weight = (((weight - offset)/15))

        return normalized_weight
