import pytest

from ..receiver import Rx


def test_receiver_should_get_messages(receiver, kernel_publish):
    globals()['received_msg'] = False
    def on_message(x, y, z):
        globals()['received_msg'] = True
    receiver.client.on_message = on_message
    kernel_publish("test")
    assert globals()['received_msg'] == True
