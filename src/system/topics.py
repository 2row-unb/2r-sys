"""
Module to define Gabby topics
"""
import gabby


_topics = gabby.TopicCollection(
    gabby.Topic('kernel_receiver', 'f'*23),
    gabby.Topic('receiver_controller', 'f'*23),
    gabby.Topic('controller_transmitter', 'f'*23),
    gabby.Topic('transmitter_kernel', 'f'*23),
    gabby.Topic('controller_processor', 'f'*18),
    gabby.Topic('processor_controller', 'f'*15),
)


def get_topics(*args):
    """
    Get a list of topics that match

    Args:
        *topic_names (str):

    Example:
        >>> get_topics("kernel_receiver", "transmitter_kernel")
        [..., ...]
    """
    return [_topics.find_by(name=arg) for arg in args]
