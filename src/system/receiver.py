import paho.mqtt.client as mqtt
import time
import logging

from .config import settings


def on_connect(client, userdata, flags, rc):
    """
    The callback for when the client receives a CONNACK response
    from the server.
    """
    logging.info(f'Connected with Mosquitto Server: (code) {rc}')

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(settings.MQTT_2RE_KERNEL_TOPIC)
    logging.debug(f'Subscribed the {settings.MQTT_2RE_KERNEL_TOPIC} topic')


def on_message(client, userdata, msg):
    """
    The callback for when a PUBLISH message is received from the server.
    """
    logging.debug(f'Received message on {msg.topic}: '
                  f'{msg.payload.decode("utf-8")}')

    #[FIXME] should clean and normalize data
    time.sleep(3)


def run():
    """
    Run the MQTT client to receive 2RE-Kernel informations
    """
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(
        settings.MQTT_2RE_KERNEL_URL, settings.MQTT_2RE_KERNEL_PORT, 60
    )

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()
