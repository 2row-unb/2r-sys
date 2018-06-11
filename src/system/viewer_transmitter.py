"""
Transmitter for 2RE KERNEL module
"""
import logging
import gabby
import requests
from .config.settings import VIEWER_API_URL


class ViewerTransmitter(gabby.Gabby):
    """
    Class to receive messages from 2RS-Controller and serialize to transmit
    to 2RS-Viewer
    """
    def transform(self, message):
        """
        Transform data to viewer
        """
        self.post(message.data)
        return []

    def post(self, data):
        """
        Post data to a viewer socket
        """
        logging.debug("Sending http request to Viewer")
        try:
            headers = {
                'Content-type': 'application/json'
            }
            requests.post(
                VIEWER_API_URL,
                json={'values': data},
                headers=headers
            )
        except Exception:
            logging.error("Failed sending message to Viewer")
        else:
            logging.debug("Success sending message to Viewer")
