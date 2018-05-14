"""
Module to transmit data to 2RKernel
"""
from .rxtx import Rx
from .helpers import make_runner


class Transmitter(Rx):
    pass

run = make_runner(Transmitter)
