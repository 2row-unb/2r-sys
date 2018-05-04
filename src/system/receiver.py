"""
Receive messages from 2RE Kernel
"""
import logging
import paho.mqtt.client as mqtt

from .config import settings


def run():
    """
    Run the MQTT client to receive 2RE-Kernel informations
    """
    rx = Rx()
    rx.run()


class Rx:
    """
    Receive messages from 2RE Kernel
    """
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = Rx.on_connect
        self.client.on_message = Rx.on_message
        self.client.connect(
            settings.MQTT_2RE_KERNEL_URL, settings.MQTT_2RE_KERNEL_PORT, 60
        )

    @staticmethod
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


    @staticmethod
    def on_message(client, userdata, msg):
        """
        The callback for when a PUBLISH message is received from the server.
        """
        logging.debug(f'Received message on {msg.topic}: '
                      f'{msg.payload.decode("utf-8")}')

        tx = Tx()
        tx.publish(msg.payload.decode("utf-8"))


    def run(self):
        """
        Blocking call that processes network traffic, dispatches callbacks and
        handles reconnecting.
        Other loop*() functions are available that give a threaded interface
        and a manual interface.
        """
        self.client.loop_forever()


class Tx:
    """
    Singleton to receiver transmitter
    """
    _instance = None

    def __new__(cls):
        if Tx._instance is None:
            Tx._instance = object.__new__(cls)
        return Tx._instance

    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = Tx.on_connect
        self.client.connect(settings.MQTT_2RS_URL, settings.MQTT_2RS_PORT, 60)

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        """
        The callback for when the client receives a CONNACK response
        from the server.
        """
        logging.info(f'Connected with Mosquitto Server: (code) {rc}')

    def publish(self, data):
        """
        Publish message to the 2RSystem controller queue
        """
        logging.debug(f'Publish on {settings.MQTT_2RS_CONTROLLER_TOPIC}')
        self.client.publish(settings.MQTT_2RS_CONTROLLER_TOPIC, data)
