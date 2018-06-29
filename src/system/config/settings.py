"""
Global configurations of 2RSystem
"""

import os

MOSQUITTO_URL = '192.168.1.100'
MOSQUITTO_PORT = 1883
MOSQUITTO_KEEPALIVE = 60
N_IMUS = 1

RSMB_URL = '192.168.1.100'
RSMB_PORT = 1885

VIEWER_API_URL = 'http://localhost:5000/info'

RPI_MOCK = os.environ.get('RPI_MOCK', 'false') == 'true'
