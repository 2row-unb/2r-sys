"""
Kernel module is responsible to handle IMUs and Strain Gage
"""
import gabby
import logging
import time

from .decorators import rpi_mock
from .config.settings import RPI_MOCK

try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    logging.error("Failed importing RPi.GPIO module")
    assert RPI_MOCK is True
else:
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)


class Kernel(gabby.Gabby):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.power_level = 0
        self._setup_relays([37, 35, 33, 31])

    def transform(self, message):
        logging.info(f'Received message from {message.topic}')

        if message.topic == 'esp_kernel':
            logging.debug(f"Data: {message.payload.decode('utf-8')}")
            imu_data = [float(x) for x in
                        message.payload.decode('utf-8').split(';')]

            buttons_info = self.get_buttons()
            weight_info = self.get_weight()
            time_info = int(time.time())
            data = [*imu_data, weight_info, time_info, *buttons_info]

            return [gabby.Message(data, self.output_topics)]

        else:
            logging.info(f'Received message from controller')
            message = gabby.Message.decode(
                message.payload,
                self.input_topics.filter_by(name='controller_kernel')
            )
            logging.debug(f'Data: {message.data}')

            button_data = message.data
            self.update_weigth(button_data)

            return []

    def get_weight(self):
        DAT1 = 15
        CLK1 = 16
        DAT2 = 13
        CLK2 = 8

        strain_gages = ((DAT1, CLK1), (DAT2, CLK2))
        total_weight = sum(
            [self._get_normalized_weight(dat, clk)
             for dat, clk in strain_gages]
        )
        power = total_weight*9.81*0.7071

        return power

    @rpi_mock([1, 1, 1])
    def get_buttons(self):
        # [FIXME] implements button debounce
        _BUTTON_UP = 18
        _BUTTON_DOWN = 11
        _BUTTON_RESET = 12

        # define inputs
        GPIO.setup(_BUTTON_UP, GPIO.IN)
        GPIO.setup(_BUTTON_DOWN, GPIO.IN)
        GPIO.setup(_BUTTON_RESET, GPIO.IN)

        return [
            GPIO.input(_BUTTON_UP),
            GPIO.input(_BUTTON_DOWN),
            GPIO.input(_BUTTON_RESET),
        ]

    @rpi_mock(10.0)
    def _get_normalized_weight(self, dat, clk):
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
        normalized_weight = (((weight - 5943)/15))

        return normalized_weight

    @rpi_mock
    def _turn(self, pins, state):
        if isinstance(pins, list):
            for i in pins:
                GPIO.output(i, state)
        else:
            GPIO.output(pins, state)

    @rpi_mock
    def update_weigth(self, button_data):
        _ON = 0
        _OFF = 1
        power_level, = button_data

        self._turn(self.RELAYS_PINS, _OFF)
        if power_level > 0 and power_level <= 4:
            self._turn(self.RELAYS_PINS[power_level - 1], _ON)

    @rpi_mock
    def _setup_relays(self, pins):
        self.RELAYS_PINS = pins
        for relay_pin in self.RELAYS_PINS:
            GPIO.setup(relay_pin, GPIO.OUT)
