import pytest

from ..message import Message

class TestController:
    def test_should_get_messages_from_receiver(
            self, controller, kernel_publish):
        globals()['controller_received_msg'] = None

        def on_message(x, y, msg):
            globals()['controller_received_msg'] = Message(msg.payload)

        controller.client.on_message = on_message
        kernel_publish(Message("test"))

        assert globals()['controller_received_msg'].data == "test"

    def test_controller_should_send_messages_to_processer(self):
        pass

    def test_controller_should_send_messages_to_transmitter(self):
        pass

    def test_controller_should_post_to_viewer(self):
        pass
