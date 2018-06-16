"""
Module to control async execution of all 2RSystem components
"""
import logging
import gabby

from .config.settings import MOSQUITTO_URL, MOSQUITTO_PORT, MOSQUITTO_KEEPALIVE
from .controller import Controller
from .viewer_api import ViewerAPI
from .processor import Processor
from .kernel import Kernel
from .kernel_control import KernelControl
from .topics import get_topics


def get_modules():
    mosquitto_config = [MOSQUITTO_URL, MOSQUITTO_PORT, MOSQUITTO_KEEPALIVE]

    return {
        'kernel': Kernel(
            get_topics('esp_kernel'),
            get_topics('kernel_controller'),
            False,
            *mosquitto_config
        ),

        'kernelcontrol': KernelControl(
            get_topics('controller_kernelcontrol'),
            get_topics('kernelcontrol_controller'),
            True,
            *mosquitto_config
        ),

        'controller': Controller(
            get_topics(
                'kernel_controller',
                'kernelcontrol_controller',
                'processor_controller'
            ),
            get_topics(
                'controller_transmitter',
                'controller_processor',
                'controller_kernelcontrol'
            ),
            True,
            *mosquitto_config
        ),

        'transmitter': ViewerAPI(
            get_topics('controller_transmitter'),
            None, True,
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
