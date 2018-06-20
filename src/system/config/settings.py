"""
Global configurations of 2RSystem
"""

import os

MOSQUITTO_URL = 'localhost'
MOSQUITTO_PORT = 1883
MOSQUITTO_KEEPALIVE = 60
N_IMUS = 1

VIEWER_API_URL = 'http://localhost:5000/info'

RPI_MOCK = os.environ.get('RPI_MOCK', 'false') == 'true'
