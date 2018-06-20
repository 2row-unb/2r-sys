"""
Module to define some system states
"""
from collections import defaultdict


class MetaState(type):
    def __new__(mcs, clsname, bases, dct):
        _names = defaultdict(lambda: 'INVALID')
        for attr_name, attr_value in dct.items():
            if not attr_name.startswith('__'):
                _names[attr_value] = attr_name

        dct['_names'] = _names
        return type.__new__(mcs, clsname, bases, dct)

    def name(cls, state):
        return cls._names[state]


class State(metaclass=MetaState):
    """
    State of processing IMU data
    """
    INITIAL = 1
    RUNNING = 2
