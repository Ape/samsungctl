import base64
import json
import logging
import threading
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
            path = os.path.join(os.path.expandvars('%appdata%'), 'samsungctl')

        else:
            path = os.path.join(os.path.expanduser('~'), '.samsungctl')

        if not os.path.exists(path):
            os.mkdir(path)

        token_file = os.path.join(path, "token.txt")

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
        self.connection = None

        def do():
            ws = websocket.WebSocketApp(
                url,
                on_close=self.on_close,
                on_open=self.on_open,
                on_error=self.on_error,
                on_message=self.on_message
            )
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

        self.open_event = threading.Event()
        self.auth_event = threading.Event()
        self.receive_event = threading.Event()
        self.receive_lock = threading.Lock()
        self.close_event = threading.Event()

        threading.Thread(target=do).start()

        self.open_event.wait(3.0)
        if not self.open_event.isSet():
            raise RuntimeError('Connection Failure')

        self.auth_event.wait(3.0)
        if not self.auth_event.isSet():
            self.close()
            raise RuntimeError('Auth Failure')

    def on_open(self, ws):
        logging.debug('Websocket Connection Opened')
        self.connection = ws
        self.open_event.set()

    def on_close(self, _):
        logging.debug('Websocket Connection Closed')
        self.connection = None
        self.close_event.set()

    def on_error(self, _, error):
        logging.error(error)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        """Close the connection."""
        if self.connection:
            with self.receive_lock:
                self.connection.close()
                self.close_event.wait(2.0)

                if not self.close_event.isSet():
                    raise RuntimeError('Close Failure')

    def control(self, key):
        """Send a control command."""
        if not self.connection:
            raise exceptions.ConnectionClosed()

        with self.receive_lock:

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
            self.receive_event.clear()
            self.connection.send(payload)
            self.receive_event.wait(2.0)

            if not self.receive_event.isSet():
                raise RuntimeError('Receive Failure')

    _key_interval = 0.5

    def on_message(self, _, message):
        response = json.loads(message)
        logging.debug(message)

        if response["event"] == "ms.channel.connect":
            if 'data' in response and 'token' in response["data"]:
                token = self.config['host'] + ':' + response['data']["token"]
                with open(self.token_file, "r") as token_file:
                    token_data = token_file.read()

                if token not in token_data:
                    with open(self.token_file, "a") as token_file:
                        token_file.write(token + '\n')

                    logging.debug("Access granted.")
                    self.auth_event.set()

        else:
            self.receive_event.set()

    @staticmethod
    def _serialize_string(string):
        if isinstance(string, str):
            string = str.encode(string)

        return base64.b64encode(string).decode("utf-8")
