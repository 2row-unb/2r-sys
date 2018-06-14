"""
Class to handle buttons end measures made by kernel
"""
import gabby

from .decorators import rpi_mock


class KernelControl(gabby.Gabby):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.power_level = 0
        self._setup_relays([37, 35, 33, 31])

    def transform(self, message):
        if message.topic == 'controller_kernelcontrol':
            work_on_message_from_controller(message)

    def work_on_message_from_controller(self, message):
        """
        Method to work on data received from ESP (2RE-Suit)
        """
        message = gabby.Message.decode(
            message.payload,
            self.input_topics.filter_by(name='controller_kernel')
        )
        logging.debug(f'Data: {message.data}')

        button_data = message.data
        self.update_power_level(button_data)

        return []

    @rpi_mock(lambda: [random.randint(0, 1), random.randint(0, 1), 1])
    def get_buttons(self):
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

        logging.warning(f'Changing power level to {power_level}')

        self._turn(self.RELAYS_PINS, _OFF)
        if power_level >= 0 and power_level < 3:
            self._turn(self.RELAYS_PINS[power_level], _ON)

    @rpi_mock
    def _setup_relays(self, pins):
        self.RELAYS_PINS = pins
        for relay_pin in self.RELAYS_PINS:
            GPIO.setup(relay_pin, GPIO.OUT)
