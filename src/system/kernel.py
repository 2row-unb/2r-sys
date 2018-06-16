"""
Kernel module is responsible to handle IMUs and Strain Gage
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


class Kernel(gabby.Gabby):
    def __init__(self, *args, **kwargs):
        self.weight_info = 0
        super().__init__(*args, **kwargs)

    def transform(self, message):
        logging.info(f'Received message from {message.topic}')

        if message.topic == 'esp_kernel':
            logging.debug(f"Data: {message.payload.decode('utf-8')}")
            imu_data = [float(x) for x in
                        message.payload.decode('utf-8').split(';')]

            controller_data = [*imu_data, self.weight_info, time.time()]
            return [
                gabby.Message(
                    controller_data,
                    self.output_topics.filter_by(name='kernel_controller')
                )
            ]
        return []

    def run(self):
        _thread.start_new_thread(self.update_weight_info, tuple())
        super().run()

    def update_weight_info(self):
        for new_info in self.get_weight():
            self.weight_info = new_info

    def get_weight(self):
        DAT1 = 15
        CLK1 = 16
        DAT2 = 13
        CLK2 = 8

        while True:
            strain_gages = ((DAT1, CLK1), (DAT2, CLK2))
            total_weight = sum(
                [self._get_normalized_weight(dat, clk)
                 for dat, clk in strain_gages]
            )
            power = total_weight*9.81*0.7071

            yield power
            time.sleep(0.3)

    @rpi_mock(lambda: random.random() * 80)
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
