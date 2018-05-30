"""
Module to control async execution of all 2RSystem components
"""
import logging
import gabby

from .config.settigs import MOSQUITTO_URL, MOSQUITTO_PORT, MOSQUITTO_KEEPALIVE
from .receiver import Receiver
from .controller import Controller
from .transmitter import Transmitter
from .processor import Processor
from .topics import get_topics


_mosquitto_config = [MOSQUITTO_URL, MOSQUITTO_PORT, MOSQUITTO_KEEPALIVE]

_modules = {
    'receiver': Receiver(
        get_topics('kernel_receiver'),
        get_topics('receiver_controller'),
        *_mosquitto_config
    ),

    'controller': Controller(
        get_topics('receiver_controller', 'processor_controller'),
        get_topics('controller_transmitter', 'controller_processor'),
        *_mosquitto_config
    ),

    'transmitter': Transmitter(
        get_topics('controller_transmitter'),
        get_topics('transmitter_kernel'),
        *_mosquitto_config
    ),

    'processor': Processor(
        get_topics('controller_processor'),
        get_topics('processor_controller'),
        *_mosquitto_config
    ),
}


def start(instance=None):
    """
    Run a process for each 2RSystem sub module
    """
    control = gabby.Controller()

    if instance is not None:
        logging.info(f'Add {instance} to System Control')
        control.add_gabby(_modules[instance])
    else:
        for k, v in _modules.items():
            logging.info(f'Add {k} to System Control')
            control.add_gabby[v]

    control.run()
