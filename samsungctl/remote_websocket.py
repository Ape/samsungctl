import base64
import json
import logging
import socket
import time
import requests

from . import exceptions

class RemoteWebsocket():
    """Object for remote control connection."""
    _config = None

    def __init__(self, config):
        import websocket

        if not config["port"]:
            config["port"] = 8001

        if config["timeout"] == 0:
            config["timeout"] = None
        self._config = config
        URL_FORMAT = "ws://{}:{}/api/v2/channels/samsung.remote.control?name={}"

        """Make a new connection."""
        self.connection = websocket.create_connection(URL_FORMAT.format(config["host"], config["port"],
                                                  self._serialize_string(config["name"])), config["timeout"])

        self._read_response()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        """Close the connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logging.debug("Connection closed.")

    def control(self, key):
        """Send a control command."""
        if not self.connection:
            raise exceptions.ConnectionClosed()

        payload = json.dumps({
            "method": "ms.remote.control",
            "params": {
                "Cmd": "Click",
                "DataOfCmd": key,
                "Option": "false",
                "TypeOfRemote": "SendRemoteKey"
            }
        })

        logging.info("Sending control command: %s", key)
        self.connection.send(payload)
        time.sleep(self._key_interval)

    _key_interval = 1.0

    def is_tv_on(self):
        url = "http://{}:{}/api/v2/"
        url = url.format(self._config['host'], self._config['port'])
        try:
            res = requests.get(url, timeout=5)
        except (requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.HTTPError,
                requests.exceptions.ReadTimeout):
            return False
        if res is not None and res.status_code == 200:
            return True
        else:
            return False

    def _read_response(self):
        response = self.connection.recv()
        response = json.loads(response)

        if response["event"] != "ms.channel.connect":
            self.close()
            raise exceptions.UnhandledResponse(response)

        logging.debug("Access granted.")

    @staticmethod
    def _serialize_string(string):
        if isinstance(string, str):
            string = str.encode(string)

        return base64.b64encode(string).decode("utf-8")
