"""
Module to define Gabby topics
"""
import gabby


_topics = {
   "kernel_receiver":           gabby.Topic('2rs/receiver/input', 'i'*23),
   "receiver_controller":       gabby.Topic('2rs/receiver/output', 'i'*23),
   "controller_transmitter":    gabby.Topic('2rs/trasmitter/input', 'i'*23),
   "trasmitter_kernel":         gabby.Topic('2rs/transmitter/output', 'i'*23),
   "controller_processor":      gabby.Topic('2rs/processor/input', 'i'*23),
   "processor_controller":      gabby.Topic('2rs/processor/output', 'i'*23),
}


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
        match_topics.extend([v for k, v in _topics.items() if k == arg])

    return match_topics
