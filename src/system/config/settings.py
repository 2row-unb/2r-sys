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

    processor = dict(
        INPUT_TOPIC="2rs/processor/input",
        OUTPUT_TOPIC="2rs/processor/output",
    )

    transmitter = dict(
        INPUT_TOPIC="2rs/transmitter/input",
        OUTPUT_TOPIC="2rs/transmitter/output",
    )

    receiver = dict(
        INPUT_TOPIC="2rs/receiver/input",
        OUTPUT_TOPIC="2rs/receiver/output",
    )

    @classmethod
    def named_config(cls, section, data):
        return section, cls.__dict__[section][data]
