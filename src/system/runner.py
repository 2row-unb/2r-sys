"""
Module to control async execution of all 2RSystem components
"""
import logging
import gabby

from .config.settings import (
    MOSQUITTO_URL, MOSQUITTO_PORT, MOSQUITTO_KEEPALIVE, RSMB_URL, RSMB_PORT
)
from .controller import Controller
from .viewer_api import ViewerAPI
from .processor import Processor
from .kernel import Kernel
from .kernel_control import KernelControl
from .topics import get_topics


def get_modules():
    hosts_config = (
        MOSQUITTO_URL, MOSQUITTO_PORT, MOSQUITTO_KEEPALIVE,
        RSMB_URL, RSMB_PORT,
    )

    return {
        'kernel': Kernel(
            get_topics('ek', 'kernelcontrol_kernel'),
            get_topics('kernel_controller'),
            False,
            *hosts_config,
            transmission=['udp', 'tcp']
        ),

        'kernelcontrol': KernelControl(
            get_topics('controller_kernelcontrol'),
            get_topics('kernelcontrol_controller', 'kernelcontrol_kernel'),
            True,
            *hosts_config,
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
            *hosts_config,
        ),

        'transmitter': ViewerAPI(
            get_topics('controller_transmitter'),
            None, True,
            *hosts_config
        ),

        'processor': Processor(
            get_topics('controller_processor'),
            get_topics('processor_controller'),
            True,
            *hosts_config
        ),
    }


def start(instance=None, exc=[]):
    """
    Run a process for each 2RSystem sub module
    """
    control = gabby.Controller()

    if instance is not None:
        logging.info(f'Add {instance} to System Control')
        control.add_gabby(get_modules()[instance])
    else:
        for k, v in get_modules().items():
            if k not in exc:
                logging.info(f'Add {k} to System Control')
                control.add_gabby(v)

    control.run()
