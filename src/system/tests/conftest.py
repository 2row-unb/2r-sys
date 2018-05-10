import pytest
import time
import paho.mqtt.client as mqtt

from . import helpers
from ..config.settings import MQTTConfig
from ..rxtx import Rx, Tx
from ..receiver import Receiver


@pytest.fixture
def kernel_receiver():
    return Receiver()


@pytest.fixture
def kernel_publisher():
    output_topics = [
        MQTTConfig.named_config('receiver', 'INPUT_TOPIC'),
    ]
    return Tx(dict(output_topics))


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
