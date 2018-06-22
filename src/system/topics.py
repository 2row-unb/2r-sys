"""
Module to define Gabby topics
"""
import gabby


_topics = gabby.TopicCollection(
    # (double)    1 - 18 : IMU data.
    # esp_kernel topic
    gabby.Topic('ek', 'd'*18, 'udp'),

    # (double)    1 - 18 : IMU data
    # (double)   19      : Power
    # (double)   20      : Timestamp
    # kernel_controller
    gabby.Topic('kc', 'd'*20, 'udp'),

    # (int)      1 - 3  : Buttons
    gabby.Topic('kernelcontrol_controller', 'i'*3),

    # (int)      1      : Weight Level
    gabby.Topic('controller_kernelcontrol', 'i'),

    # (double)    1 - 7  : Angles and Quaternions
    # (double)    8      : Power
    # (double)    9      : State
    # (double)   10      : Timestamp
    # [TODO] Put state as an integer
    gabby.Topic('controller_transmitter', 'd'*10),
    # (double)    1 - 18 : IMU Data
    # (double)   19      : Power
    # (int)      20      : State
    # (double)   21      : Timestamp
    # [TODO] Put state as an integer
    gabby.Topic('controller_processor', 'd'*21),

    # (double)    1 - 7  : Angles and Quaternions
    # (double)    8      : Power
    # (double)    9      : State
    # (double)   10      : Timestamp
    # [TODO] Put state as an integer
    gabby.Topic('processor_controller', 'd'*10),
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
    return gabby.TopicCollection([_topics.find_by(name=arg) for arg in args])
