"""
Module to filter and process all data
"""
from .rxtx import Rx
from .helpers import make_runner


class Processor(Rx):
    pass


run = make_runner(Processor)
