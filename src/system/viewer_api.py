"""
Transmitter for 2RE KERNEL module
"""
import logging
import gabby
import _thread
from functools import partial
from flask import Flask, jsonify


registered_routes = {}


def register_route(route=None):
    """
    Simple decorator for class based views
    """
    def inner(fn):
        registered_routes[route] = fn
        return fn
    return inner


class ViewerAPI(gabby.Gabby, Flask):
    """
    Class to receive messages from 2RS-Controller and serialize to transmit
    to 2RS-Viewer
    """
    def __init__(self, *args, **kwargs):
        gabby.Gabby.__init__(self, *args, **kwargs)
        Flask.__init__(self, ViewerAPI.__name__)
        self.info = None

        for route, fn in registered_routes.items():
            partial_fn = partial(fn, self)
            partial_fn.__name__ = fn.__name__
            self.route(route)(partial_fn)

    def run(self):
        _thread.start_new_thread(Flask.run, (self,), {
            'debug': False, 'host': '0.0.0.0'
        })
        gabby.Gabby.run(self)

    def transform(self, message):
        """
        Transform data to viewer
        """
        self.update_info(message.data)
        return []

    def update_info(self, data):
        """
        Post data to a viewer socket
        """
        logging.debug("Updating angles information")
        self.info = data

    @register_route('/angles')
    def angles_view(self):
        angles = self.info[0:3]

        response = {
            'status': 'ok',
            'errors': [],
            'state': 2,
            'athlete': {
                'l_thigh_1': angles
            },
            'power': 400,
            'speed': 33,
            'timer': 122,
            'difficulty': 2
        } if self.info else {
            'status': 'fail',
            'errors': ['Information unavailable']}

        return jsonify(response)
