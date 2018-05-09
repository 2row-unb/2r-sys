import pytest
import time
from . import helpers
import paho.mqtt.client as mqtt

from ..config import settings
from ..rxtx import Rx, Tx
from ..receiver import Receiver


@pytest.fixture
def kernel_receiver():
    return Receiver()


@pytest.fixture
def kernel_publisher():
    return Tx([settings.MQTT_2RE_KERNEL_TOPIC])


@pytest.fixture
def kernel_publish(kernel_publisher):
    return lambda msg: (lambda _:(time.sleep(0.2))
    )(kernel_publisher.publish(msg))


@pytest.fixture(autouse=True)
def receiver(kernel_receiver):
    receiver = kernel_receiver
    th = helpers.start_receiver(receiver)
    yield kernel_receiver  # provide the fixture value
    helpers.stop_receiver(th)
