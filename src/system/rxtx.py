"""
Base for transmitters and receivers classes
"""
import logging
import paho.mqtt.client as mqtt

from .config.settings import MQTTConfig


class Rx:
    """
    Receive messages from specific mqtt queue

    Args:
        url (str):
            mqtt server URL
        port (int):
            mqtt server port
        topics (list):
            list of strings with the topic names

    Example:
        >>> class receiver(Rx):
        ...     def on_message(self):
        ...         def wrap(client, userdata, message):
        ...             print(message.payload.decode("utf-8")
        ...     return wrap
    """
    _url = MQTTConfig.general['URL']
    _port = MQTTConfig.general['PORT']

    def __init__(self, topics):
        self.running = True
        self.topics = topics
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect()
        self.client.on_message = self._on_message()
        self.client.connect(Rx._url, Rx._port, 60)

    def _on_connect(self):
        """
        The callback for when the client receives a CONNACK response
        from the server.
        """
        def wrap(client, userdata, flags, rc):
            logging.info(f'Connected with Mosquitto Server: (code) {rc}')
            self.subscribe(self.topics)
        return wrap

    def _on_message(self):
        """
        The callback for when a PUBLISH message is received from the server.
        """
        raise NotImplementedError

    def run(self):
        """
        Blocking call that processes network traffic, dispatches callbacks and
        handles reconnecting.
        Other loop*() functions are available that give a threaded interface
        and a manual interface.
        """
        while self.running:
            self.client.loop()

    def subscribe(self, topics):
        """
        Subscribe to a list of channels

        Args:
            topics (list):
                list of topics to subscribe the mqtt listener
        """
        for topic in topics:
            try:
                self.client.subscribe(topic)
                logging.debug(f'Subscribed the {topic} topic')
            except:
                logging.debug(f"Can't subscribe the {topic} topic")

    def stop(self):
        """
        Stop running
        """
        self.running = False


class Tx:
    """
    Handler for MQTT publishing

    Args:
        topics (dict):
            keys identify the topic, values for the mqtt topic names to publish
    """
    _url = MQTTConfig.general['URL']
    _port = MQTTConfig.general['PORT']

    def __init__(self, topics):
        self.topics = topics
        self.client = mqtt.Client()
        self.client.on_connect = Tx.on_connect
        self.client.connect(Tx._url, Tx._port, 60)

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        """
        The callback for when the client receives a CONNACK response
        from the server.
        """
        logging.debug(f'Connected with Mosquitto Server: (code) {rc}')

    def publish(self, message):
        """
        Publish message to the 2RSystem queue

        Args:
            data (Message):
                Message to publish
        """
        if message.to in self.topics.keys():
            logging.debug(f'Publishing on {self.topics[message.to]}')
            self.client.publish(self.topics[message.to], message.encoded)
        elif not message.to:
            for _, topic in self.topics.items():
                logging.debug(f'Publishing on {topic}')
                self.client.publish(topic, message.encoded)
        else:
            logging.error(f'Error publishing on {message.to}')
