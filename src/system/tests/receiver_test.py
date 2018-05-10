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


def test_should_not_process_others_messages(receiver, kernel_publish):
    globals()['received_msg'] = None

    def on_message(x, y, msg):
        message = Message(msg.payload)
        if message.to == 'receiver':
            globals()['received_msg'] = Message(msg.payload)

    receiver.client.on_message = on_message
    kernel_publish(Message("test", to='someone'))

    assert globals()['received_msg'] is None


def test_should_process_signed_messages(receiver, kernel_publish):
    globals()['received_msg'] = None

    def on_message(x, y, msg):
        message = Message(msg.payload)
        if message.to == 'receiver':
            globals()['received_msg'] = Message(msg.payload)

    receiver.client.on_message = on_message
    kernel_publish(Message("test", to='receiver'))

    assert globals()['received_msg'].data == "test"
