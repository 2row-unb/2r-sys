"""
Module to control async execution of all 2RSystem components
"""
import logging
import gabby

from .config.settings import MOSQUITTO_URL, MOSQUITTO_PORT, MOSQUITTO_KEEPALIVE
from .receiver import Receiver
from .controller import Controller
from .transmitter import Transmitter
from .processor import Processor
from .topics import get_topics


def get_modules():
    mosquitto_config = [MOSQUITTO_URL, MOSQUITTO_PORT, MOSQUITTO_KEEPALIVE]

    return {
        'receiver': Receiver(
            get_topics('kernel_receiver'),
            get_topics('receiver_controller'),
            False,
            *mosquitto_config
        ),

        'controller': Controller(
            get_topics('receiver_controller', 'processor_controller'),
            get_topics('controller_transmitter', 'controller_processor'),
            True,
            *mosquitto_config
        ),

        'transmitter': Transmitter(
            get_topics('controller_transmitter'),
            get_topics('transmitter_kernel'),
            True,
            *mosquitto_config
        ),

        'processor': Processor(
            get_topics('controller_processor'),
            get_topics('processor_controller'),
            True,
            *mosquitto_config
        ),
    }


def start(instance=None):
    """
    Run a process for each 2RSystem sub module
    """
    control = gabby.Controller()

    if instance is not None:
        logging.info(f'Add {instance} to System Control')
        control.add_gabby(get_modules()[instance])
    else:
        for k, v in get_modules().items():
            logging.info(f'Add {k} to System Control')
            control.add_gabby(v)

    control.run()
