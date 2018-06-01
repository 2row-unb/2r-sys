"""
Module to define Gabby topics
"""
import gabby


_topics = (
    gabby.Topic('kernel_receiver', '2rs/receiver/input', 'f'*23),
    gabby.Topic('receiver_controller', '2rs/receiver/output', 'f'*23),
    gabby.Topic('controller_transmitter', '2rs/trasmitter/input', 'f'*23),
    gabby.Topic('transmitter_kernel', '2rs/transmitter/output', 'f'*23),
    gabby.Topic('controller_processor', '2rs/processor/input', 'f'*18),
    gabby.Topic('processor_controller', '2rs/processor/output', 'f'*15),
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
    match_topics = []
    for arg in args:
        match_topics.extend([t for t in _topics if t.alias == arg])

    return match_topics
