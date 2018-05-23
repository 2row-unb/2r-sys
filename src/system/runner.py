"""
Module to control async execution of all 2RSystem components
"""
import logging
from multiprocessing import Process

from .receiver import run as receiver_run
from .controller import run as controller_run
from .transmitter import run as transmitter_run
from .processor import run as processor_run


PROC_FUNCS = {
    'Receiver': receiver_run,
    'Controller': controller_run,
    'Processor': processor_run,
    'Transmitter': transmitter_run,
}


def start(instance=None):
    """
    Run a process for each 2RSystem sub module
    """
    runner_procs = [run_instance(k, v) for k, v in PROC_FUNCS.items()
                    if not instance or k == instance.capitalize()]

    for proc in runner_procs:
        proc.join()

    logging.info("[Success] Shutted down")


def run_instance(name, func):
    """
    Start a new process to execute a given function
    """
    logging.info(f'Starting {name}')
    proc = Process(target=func)
    proc.start()
    return proc
