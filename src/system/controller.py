"""
2RS Controller
"""
import pickle

from .config.settings import MQTTConfig
from .rxtx import Rx, Tx

class Controller(Rx):
    def __init__(self):
        input_topics = (
            MQTTConfig.receiver['OUTPUT_TOPIC'],
            MQTTConfig.processor['OUTPUT_TOPIC'],
        )
        super().__init__(input_topics)

        output_topics = (
            MQTTConfig.named_config('transmitter', 'INPUT_TOPIC'),
        )
        self.tx = Tx(dict(output_topics))

    def _on_message(self):
        def wrap(client, userdata, message):
            self.tx.publish(self.format(message))
        return wrap

    def format(self, message):
        """
        Format mqtt messages
        """
        data = pickle.dumps(message)
        print(str(data))
        return pickle.loads(data)
