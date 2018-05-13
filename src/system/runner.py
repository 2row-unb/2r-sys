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
    '2RS-Receiver': receiver_run,
    '2RS-Controller': controller_run,
    '2RS-Processor': processor_run,
    '2RS-Transmitter': transmitter_run,
}


def start():
    """
    Run a process for each 2RSystem sub module
    """
    runner_procs = [run_instance(*kv) for kv in PROC_FUNCS.items()]

    for proc in runner_procs:
        proc.join()

    logging.info("All system shutted down")

def run_instance(name, func):
    """
    Start a new process to execute a given function
    """
    logging.info(f'Starting {name}')
    proc = Process(target=func)
    proc.start()
    return proc
