import pytest
import time
from . import helpers
import paho.mqtt.client as mqtt

from ..config import settings
from ..receiver import Rx

@pytest.fixture
def mqtt_client():
    return mqtt.Client()


@pytest.fixture
def mqtt_kernel_client(mqtt_client):
    mqtt_client.connect(
        settings.MQTT_2RE_KERNEL_URL,
        settings.MQTT_2RE_KERNEL_PORT,
        60
    )
    mqtt_client.subscribe(settings.MQTT_2RE_KERNEL_TOPIC)
    return mqtt_client


@pytest.fixture
def mqtt_kernel_publish(mqtt_kernel_client):
    return lambda msg: (lambda _:(time.sleep(0.2))
    )(mqtt_kernel_client.publish(settings.MQTT_2RE_KERNEL_TOPIC, msg))


@pytest.fixture(scope="module", autouse=True)
def mqtt_receiver():
    global rx
    rx = Rx()
    th = helpers.start_receiver(rx)
    yield mqtt_receiver  # provide the fixture value
    helpers.stop_receiver(th)


@pytest.fixture
def receiver():
    global rx
    return rx
