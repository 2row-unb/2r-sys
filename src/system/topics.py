"""
Module to define Gabby topics
"""
import gabby


_topics = gabby.TopicCollection(
    # (double)    1 - 18 : IMU data.
    gabby.Topic('esp_kernel', 'd'*18),

    # (double)    1 - 18 : IMU data
    # (double)   19      : Power
    # (int)     20 - 22 : Buttons
    # (double)   23      : Timestamp
    gabby.Topic('kernel_controller', 'd'*19 + 'i'*3 + 'd'),

    # (int)      1      : Weight Level
    gabby.Topic('controller_kernel', 'i'),

    # (double)    1 - 15 : Angles
    # (double)    16     : Power
    # (double)    17     : Timestamp
    gabby.Topic('controller_transmitter', 'd'*17),

    # (double)    1 - 18 : IMU Data
    # (double)   19      : Weight
    # (double)   20      : Timestamp
    gabby.Topic('controller_processor', 'd'*20),

    # (double)    1 - 15 : Angles
    # (double)   16      : Weight
    # (double)   17      : Timestamp
    gabby.Topic('processor_controller', 'd'*17),
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
