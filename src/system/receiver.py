"""
Receiver for 2RE KERNEL module
"""

from .rxtx import Rx, Tx
from .config.settings import MQTTConfig


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
        topics = (MQTTConfig.receiver['INPUT_TOPIC'],)
        super().__init__(topics)

        self.tx = Tx((MQTTConfig.receiver['OUTPUT_TOPIC'],))

    def _on_message(self):
        def wrap(client, userdata, message):
            self.tx.publish(self.format(message))
        return wrap

    def format(self, message):
        """
        Format mqtt messages
        """
        return message.payload.decode("utf-8")
