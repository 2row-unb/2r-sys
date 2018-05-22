"""
Base for transmitters and receivers classes
"""
import logging
import paho.mqtt.client as mqtt

from .config.settings import MQTTConfig
from .decorators import on_connect


class MQTTClient(type):
    """
    Metaclass to handle MQTT methods and connections

    Inheriting from this class it is possible to use decorators:
        - @on_connect:
            Decorate method to respond to MQTT Client connections

        - @on_message:
            Decorate method to respond to MQTT Client received messages

    Example:
        >>> class Receptor(metaclass=MQTTClient):
        ...     pass
    """
    _url = MQTTConfig.general['URL']
    _port = MQTTConfig.general['PORT']

    def __call__(cls, *args, **kwargs):
        obj = super(MQTTClient, cls).__call__(*args, **kwargs)
        return MQTTClient.connect(obj)

    @classmethod
    def connect(mcs, obj):
        """
        Connect new object to an MQTT client
        """
        obj.client = mqtt.Client()
        mcs.activate_on_message_hook(obj)
        mcs.activate_on_connect_hook(obj)
        obj.client.connect(MQTTClient._url, MQTTClient._port, 60)
        return obj

    @classmethod
    def activate_on_message_hook(mcs, obj):
        """
        Configure 'on_message' decorated method as default
        responding behavior
        """
        action = lambda x: setattr(obj.client, 'on_message', x)
        mcs.activate_hook(obj, 'ON_MESSAGE_DECORATOR', action)

    @classmethod
    def activate_on_connect_hook(mcs, obj):
        """
        Configure 'on_connect' decorated method as default
        connecting behavior
        """
        action = lambda x: setattr(obj.client, 'on_connect', x)
        mcs.activate_hook(obj, 'ON_CONNECT_DECORATOR', action)

    @classmethod
    def activate_hook(mcs, obj, dec_name, action):
        """
        Apply an action to the first method decorated with a
        specific decorator
        """
        hook_methods = mcs.find_decorated_methods(obj, dec_name)

        # Check there is a decorated method
        if not hook_methods:
            raise f'{dec_name} not found'

        return action(hook_methods[0])

    @classmethod
    def find_decorated_methods(mcs, obj, dec_name):
        """
        Search for methods that have been decorated
        """
        return ([
            getattr(obj, x) for x in dir(obj)
            if not x.startswith('__')
            and callable(getattr(obj, x))
            and mcs.has_decorator(obj, x, dec_name)
        ])

    @classmethod
    def has_decorator(mcs, obj, func, dec_name):
        """
        Check method is decorated
        """
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
            keys identify the topic, values for the mqtt topic
            names to publish
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
        self.write(message.encoded, message.to)

    def write(self, message, to=None):
        """
        Publish string to the 2RSystem queue

        Args:
            data (str):
                string message to publish
            to (str):
                topic name
        """
        if to in self.topics.keys():
            logging.debug(f'Publishing on {self.topics[to]}')
            self.client.publish(self.topics[to], message)
        elif to is None:
            for _, topic in self.topics.items():
                logging.debug(f'Publishing on {topic}')
                self.client.publish(topic, message)
        else:
            logging.error(f'Error publishing on {to}')
