"""
Base for transmitters and receivers classes
"""
import logging
import paho.mqtt.client as mqtt

from .config.settings import MQTTConfig
from .decorators import on_connect


class MQTTClient(type):
    _url = MQTTConfig.general['URL']
    _port = MQTTConfig.general['PORT']

    def __call__(cls, *args, **kwargs):
        obj = super(MQTTClient, cls).__call__(*args, **kwargs)
        return cls.connect(obj)

    @classmethod
    def connect(cls, obj):
        obj.client = mqtt.Client()
        cls.activate_on_message_hook(obj)
        cls.activate_on_connect_hook(obj)
        obj.client.connect(MQTTClient._url, MQTTClient._port, 60)
        return obj

    @classmethod
    def activate_on_message_hook(cls, obj):
        action = lambda x: setattr(obj.client, 'on_message', x)
        cls.activate_hook(obj, 'ON_MESSAGE_DECORATOR', action)

    @classmethod
    def activate_on_connect_hook(cls, obj):
        action = lambda x: setattr(obj.client, 'on_connect', x)
        cls.activate_hook(obj, 'ON_CONNECT_DECORATOR', action)

    @classmethod
    def activate_hook(cls, obj, dec_name, action):
        hook_methods = cls.find_decorated_methods(obj, dec_name)

        # Check there is a decorated method
        if not len(hook_methods):
            raise f'{dec_name} not found'

        return action(hook_methods[0])

    @classmethod
    def find_decorated_methods(cls, obj, dec_name):
        return ([
            getattr(obj, x) for x in dir(obj)
            if not x.startswith('__')
            and callable(getattr(obj, x))
            and cls.has_decorator(obj, x, dec_name)
        ])

    @classmethod
    def has_decorator(cls, obj, func, dec_name):
        return hasattr(getattr(obj, func), dec_name)


class Rx(metaclass=MQTTClient):
    """
    Receive messages from specific mqtt queue

    Args:
        topics (list):
            list of strings with the topic names
    """

    def __init__(self, topics):
        self.client = None
        self.running = True
        self.topics = topics

    @on_connect
    def _on_connect(self, client, userdata, flags, rc):
        """
        The callback for when the client receives a CONNACK response
        from the server.
        """
        logging.info(f'Connected with Mosquitto Server: (code) {rc}')
        self.subscribe(self.topics)

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
