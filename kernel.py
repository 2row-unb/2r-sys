"""
Kernel module is responsible to handle IMUs and Strain Gage
"""

import gabby
import logging
import RPi.GPIO as GPIO
import time

from .config.settings import BUTTONS_DEBOUNCE


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)


class Kernel(gabby.Gabby):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.power_level = 0

    def transform(self, message):
        if message.belongs_to('esp_kernel'):
            logging.debug(
                f"Received message, data: {message.payload.decode('utf-8')}")
            imu_data = [float(x) for x in
                        message.payload.decode('utf-8').split(';')]

            buttons_info = self.get_buttons()
            weight_info = self.get_weight()
            time_info = time.time()

            data = [*imu_data, time_info, *buttons_info, weight_info]
            return [gabby.Message(data, self.output_topics)]

        if message.belongs_to('transmitter_kernel'):
            logging.info(f'Received message from transmitter: {message.data}')

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

    def get_buttons(self):
        button_reset = 0

        _BUTTON_UP = 18
        _BUTTON_DOWN = 11
        _BUTTON_RESET = 12

        # define inputs
        GPIO.setup(_BUTTON_UP, GPIO.IN)
        GPIO.setup(_BUTTON_DOWN, GPIO.IN)
        GPIO.setup(_BUTTON_RESET, GPIO.IN)

        if GPIO.input(_BUTTON_UP) == 1:
            time.sleep(BUTTONS_DEBOUNCE)
            self.power_level += 1
            if (self.power_level > 4):
                self.power_level = 0

        if GPIO.input(_BUTTON_DOWN) == 1:
            time.sleep(BUTTONS_DEBOUNCE)
            self.power_level -= 1
            if (self.power_level < 0):
                self.power_level = 0

        if GPIO.input(_BUTTON_RESET) == 1:
            button_reset = 1

        return [self.power_level, button_reset]

    def _get_normalized_weight(self, dat, clk):
        GPIO.setup(clk, GPIO.OUT)

        counter = 0
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

    def _turn(self, pins, state):
        if isinstance(pins, list):
            for i in pins:
                GPIO.output(i, state)
        else:
            GPIO.output(i, state)

    def update_weigth(self, button_data):
        _ON = 0
        _OFF = 1
        power_level, = button_data

        RELAYS_PINS = [37, 35, 33, 31]

        # setup relays output pins
        for relay_pin in RELAYS_PINS:
            GPIO.setup(relay_pin, GPIO.OUT)

        self._turn(RELAYS_PINS, _OFF)
        if power_level > 0 and power_level <= 4:
            self._turn(RELAYS_PINS[power_level - 1], _ON)
