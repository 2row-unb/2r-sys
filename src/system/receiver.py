"""
Receiver for 2RE KERNEL module
"""

from .rxtx import Rx, Tx
from .config import settings


def run(receiver=None):
    """
    Run an instance of receiver
    """
    if receiver:
        receiver = Receiver()
    receiver.run()
    return receiver


class Receiver(Rx):
    def __init__(self):
        topics = [settings.MQTT_2RE_KERNEL_TOPIC]
        super().__init__(topics)

        self.tx = Tx([settings.MQTT_2RS_CONTROLLER_TOPIC])

    def _on_message(self):
        def wrap(client, userdata, message):
            self.tx.publish(self.format(message))
        return wrap

    def format(self, message):
        """
        Format mqtt messages
        """
        return message.payload.decode("utf-8")
