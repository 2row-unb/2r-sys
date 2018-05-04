"""
2RSystem module contains the following sub modules
    (receiver) 2RS-Receiver
    (transmitter) 2RS-Transmitter
    (processer) 2RS-Processer
"""
import logging
from multiprocessing import Process

from .receiver import run as receiver_run

def start():
    """
    Run a process for each 2RSystem sub module
    """
    logging.info('Starting 2RS-Receiver')
    receiver_proc = Process(target=receiver_run)
    receiver_proc.start()

    receiver_proc.join()

    logging.info("All system shutted down")
