"""
Module to define Gabby topics
"""
import gabby


_topics = gabby.TopicCollection(
    # (float)    1 - 18 : IMU data.
    gabby.Topic('esp_kernel', 'f'*18),

    # (float)    1 - 18 : IMU data
    # (float)   19      : Power
    # (int)     20 - 22 : Buttons
    # (float)   23      : Timestamp
    gabby.Topic('kernel_controller', 'f'*19 + 'i'*3 + 'f'),

    # (int)      1      : Weight Level
    gabby.Topic('controller_kernel', 'i'),

    # (float)    1 - 15 : Angles
    # (float)    16     : Power
    # (float)    17     : Timestamp
    gabby.Topic('controller_transmitter', 'f'*17),

    # (float)    1 - 18 : IMU Data
    # (float)   19      : Weight
    # (float)   20      : Timestamp
    gabby.Topic('controller_processor', 'f'*20),

    # (float)    1 - 15 : Angles
    # (float)   16      : Weight
    # (float)   17      : Timestamp
    gabby.Topic('processor_controller', 'f'*17),
)


def get_topics(*args):
    """
    Get a list of topics that match

    Args:
        *topic_names (str):

    Example:
        >>> get_topics("kernel_controller", "transmitter_kernel")
        [..., ...]
    """
    return [_topics.find_by(name=arg) for arg in args]
