"""
Global configurations of 2RSystem
"""

from collections import namedtuple

Topic = namedtuple('Topic', ['topic', 'fmt'])
Module = namedtuple('Module', ['name', 'input', 'output'])


def enum(**named_args):
    return type('MetaConfig', (), named_args)


Config = enum(
    general={
        'URL': "localhost",
        'PORT': 1883,
    },

    controller=Module('controller', None, None),

    processor=Module(
        'processor',
        Topic('2rs/processor/input', 'i'*23),
        Topic('2rs/processor/output', 'i'*23)
    ),

    transmitter=Module(
        'transmitter',
        Topic('2rs/transmitter/input', 'i'*23),
        Topic('2rs/transmitter/output', 'ffff')
    ),

    receiver=Module(
        'receiver',
        Topic('2rs/receiver/input', None),
        Topic('2rs/receiver/output', 'i'*23)
    ),
)
