"""
Global configurations of 2RSystem
"""

class MQTTConfig:
    """
    Configuration class for MQTT protocol
    """
    general = dict(
        URL="localhost",
        PORT=1883,
    )

    controller = dict(
        CODE=0,
    )

    processor = dict(
        INPUT_TOPIC="2rs/processor/input",
        OUTPUT_TOPIC="2rs/processor/output",
        CODE=1,
    )

    transmitter = dict(
        INPUT_TOPIC="2rs/transmitter/input",
        OUTPUT_TOPIC="2rs/transmitter/output",
        CODE=2,
    )

    receiver = dict(
        INPUT_TOPIC="2rs/receiver/input",
        OUTPUT_TOPIC="2rs/receiver/output",
        CODE=3,
    )

    code = {
        0: 'controller',
        1: 'processor',
        2: 'transmitter',
        3: 'receiver',
    }

    @classmethod
    def named_config(cls, section, data):
        return section, cls.__dict__[section][data]

    @classmethod
    def find_code(cls, code):
        return cls.code[code]
