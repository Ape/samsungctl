# -*- coding: utf-8 -*-

import base64
import json
import logging
import threading
import ssl
import os
import sys
import websocket
from . import exceptions


logger = logging.getLogger('samsungctl')


URL_FORMAT = "ws://{}:{}/api/v2/channels/samsung.remote.control?name={}"
SSL_URL_FORMAT = "wss://{}:{}/api/v2/channels/samsung.remote.control?name={}"


class RemoteWebsocket(websocket.WebSocketApp):
    """Object for remote control connection."""

    def __init__(self, config):
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

        self.token_file = token_file

        self.config = config

        self.open_event = threading.Event()
        self.auth_event = threading.Event()
        self.receive_event = threading.Event()
        self.receive_lock = threading.Lock()
        self.close_event = threading.Event()
        self.sock = None

        self.open()

    def on_open(self, *_):
        logger.debug('Websocket Connection Opened')
        self.open_event.set()

    def open(self):
        def do():
            token = ''
            all_tokens = []

            with open(self.token_file, 'r') as f:
                tokens = f.read()

            for line in tokens.split('\n'):
                if not line.strip():
                    continue
                if line.startswith(self.config["host"] + ':'):
                    token = line
                else:
                    all_tokens += [line]

            if token:
                all_tokens += [token]
                token = token.replace(self.config["host"] + ':', '')
                logger.debug('using saved token: ' + token)
                token = "&token=" + token

            if all_tokens:
                with open(self.token_file, 'w') as f:
                    f.write('\n'.join(all_tokens) + '\n')

            with self.receive_lock:
                if self.sock is not None:
                    self.close()

                if token or self.config['port'] == 8002:
                    self.config['port'] = 8002
                    url = SSL_URL_FORMAT.format(
                        self.config["host"],
                        self.config["port"],
                        self._serialize_string(self.config["name"])
                    ) + token

                else:
                    self.config['port'] = 8001
                    url = URL_FORMAT.format(
                        self.config["host"],
                        self.config["port"],
                        self._serialize_string(self.config["name"])
                    )

                super(RemoteWebsocket, self).__init__(url)

            if token or self.config['port'] == 8002:
                self.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
            else:
                self.run_forever()

        self.open_event.clear()
        self.auth_event.clear()
        self.receive_event.clear()

        threading.Thread(target=do).start()

        self.open_event.wait(5.0)
        if not self.open_event.isSet():
            raise RuntimeError('Connection Failure')

        self.auth_event.wait(30.0)
        if not self.auth_event.isSet():
            self.close()
            raise RuntimeError('Auth Failure')

    def on_close(self, *_):
        logger.debug('Websocket Connection Closed')

    def on_error(self, *args):
        logger.error('Websocket error: %s', args)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        """Close the connection."""
        if self.sock is not None:
            with self.receive_lock:
                websocket.WebSocketApp.close(self)

    def control(self, key, cmd='Click'):
        """
        Send a control command.
        cmd can be one of the following
        'Click'
        'Press'
        'Release'
        """
        if self.sock is None:
            raise exceptions.ConnectionClosed()

        with self.receive_lock:

            payload = json.dumps({
                "method": "ms.remote.control",
                "params": {
                    "Cmd": cmd,
                    "DataOfCmd": key,
                    "Option": "false",
                    "TypeOfRemote": "SendRemoteKey"
                }
            })

            logger.info("Sending control command: " + key)
            self.receive_event.clear()
            self.send(payload)
            self.receive_event.wait(0.35)

    _key_interval = 0.5

    def on_message(self, *args):
        if len(args) == 1:
            message = args[0]
        else:
            message = args[1]

        response = json.loads(message)
        logger.debug('incoming message: ' + message)

        if response["event"] == "ms.channel.connect":
            if 'data' in response and 'token' in response["data"]:
                token = self.config['host'] + ':' + response['data']["token"]
                with open(self.token_file, "r") as token_file:
                    token_data = token_file.read().split('\n')

                for line in token_data[:]:
                    if line.startswith(self.config['host'] + ':'):
                        token_data.remove(line)

                token_data += [token]

                logger.debug('new token: ' + token)
                with open(self.token_file, "w") as token_file:
                    token_file.write('\n'.join(token_data) + '\n')

            logger.debug("Access granted.")
            self.auth_event.set()

        elif response['event'] == 'ms.channel.unauthorized':
            if self.config['port'] == 8001:
                logger.debug(
                    "Websocket connection failed. Trying ssl connection"
                )
                self.config['port'] = 8002
                self.open()
            else:
                self.close()
                raise RuntimeError('Authentication denied')

    def start_voice_recognition(self):
        """Activates voice recognition."""
        self.control('KEY_BT_VOICE', 'Press')

    def stop_voice_recognition(self):
        """Activates voice recognition."""
        self.control('KEY_BT_VOICE', 'Release')

    @staticmethod
    def _serialize_string(string):
        if isinstance(string, str):
            string = str.encode(string)

        return base64.b64encode(string).decode("utf-8")
