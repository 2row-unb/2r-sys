import pytest

from ..receiver import Rx
from ..message import Message


def test_receiver_should_get_messages(receiver, kernel_publish):
    globals()['received_msg'] = None
    def on_message(x, y, msg):
        globals()['received_msg'] = Message(msg.payload)
    receiver.client.on_message = on_message
    kernel_publish(Message("test"))
    assert globals()['received_msg'].data == "test"
