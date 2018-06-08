"""
Module to define Gabby topics
"""
import gabby


_topics = gabby.TopicCollection(
    # (float)    1 - 18 : IMU data.
    gabby.Topic('esp_kernel', 'f'*18),

    # (float)    1 - 18 : IMU data
    # (float)   19      : Power
    # (int)     20      : Timestamp
    # (int)     21 - 23 : Buttons
    gabby.Topic('kernel_controller', 'f'*19 + 'i'*4),

    # (int)      1      : Weight Level
    gabby.Topic('controller_kernel', 'i'),

    # (float)    1 - 15 : Angles
    # (float)    16     : Power
    # (int)      17     : Timestamp
    gabby.Topic('controller_transmitter', 'f'*16 + 'i'),

    # (float)    1 - 18 : IMU Data
    # (float)   19      : Weight
    # (int)     20      : Timestamp
    gabby.Topic('controller_processor', 'f'*19 + 'i'),

    # (float)    1 - 15 : Angles
    # (float)   16      : Weight
    # (int)     17      : Timestamp
    gabby.Topic('processor_controller', 'f'*16 + 'i'),
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
