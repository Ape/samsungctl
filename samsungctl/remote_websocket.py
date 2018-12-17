import base64
import json
import logging
import socket
import threading
import time
import ssl
import os
from . import exceptions


URL_FORMAT = "ws://{}:{}/api/v2/channels/samsung.remote.control?name={}"
SSL_URL_FORMAT = "wss://{}:{}/api/v2/channels/samsung.remote.control?name={}"


class RemoteWebsocket():
    """Object for remote control connection."""

    def __init__(self, config):
        import websocket
        import sys

        if sys.platform.startswith('win'):
            path = os.path.join('%appdata%', 'samsungctl')

        else:
            path = os.path.join('~', '.samsungctl')

        path = os.path.expandvars(path)

        if not os.path.exists(path):
            os.mkdir(path)

        token_file = path + "/token.txt"
        if not os.path.exists(token_file):
            with open(token_file, 'w') as f:
                f.write('')

        with open(token_file, 'r') as f:
            tokens = f.read()

        for line in tokens.split('\n'):
            if line.startswith(config["host"]):
                token = "&token=" + line.replace(config["host"] + ':', '')
                break
        else:
            token = ''

        self.token_file = token_file

        config['port'] = 8002
        if config["timeout"] == 0:
            config["timeout"] = None

        url = SSL_URL_FORMAT.format(
            config["host"],
            config["port"],
            self._serialize_string(config["name"])
        ) + token

        self.config = config
        self.connection = websocket.create_connection(
            url,
            config["timeout"], sslopt={"cert_reqs": ssl.CERT_NONE}
        )
        self.auth_event = threading.Event()
        self._read_response()
        if not self.auth_event.isSet():
            self.close()
            raise RuntimeError('Auth Failure')

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
        self._read_response()
        time.sleep(self._key_interval)

    _key_interval = 0.5

    def _read_response(self):
        response = self.connection.recv()
        response = json.loads(response)
        logging.debug(response)

        if response["event"] == "ms.channel.connect":
            if 'data' in response and 'token' in response["data"]:
                with open(self.token_file, "a") as token_file:
                    token_file.write(
                        self.config['host'] + ':' + response['data'][
                            "token"] + '\n'
                    )
                    logging.debug("Access granted.")
                    self.auth_event.set()

    @staticmethod
    def _serialize_string(string):
        if isinstance(string, str):
            string = str.encode(string)

        return base64.b64encode(string).decode("utf-8")
