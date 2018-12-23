# -*- coding: utf-8 -*-

import base64
import json
import logging
import threading
import ssl
import os
import sys
import websocket
import time
from . import exceptions


logger = logging.getLogger('samsungctl')


URL_FORMAT = "ws://{}:{}/api/v2/channels/samsung.remote.control?name={}"
SSL_URL_FORMAT = "wss://{}:{}/api/v2/channels/samsung.remote.control?name={}"


class RemoteWebsocket(object):
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
        self.connection = None

        self.open_event = threading.Event()
        self.auth_event = threading.Event()
        self.receive_event = threading.Event()
        self.receive_lock = threading.Lock()
        self.close_event = threading.Event()
        self._receive_callbacks = []

        self.open()

    def on_open(self, ws):
        logger.debug('Websocket Connection Opened')
        self.connection = ws
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
                if line.startswith(self.config["host"]):
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
                if self.connection is not None:
                    self.connection.close()

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

                ws = websocket.WebSocketApp(
                    url,
                    on_close=self.on_close,
                    on_open=self.on_open,
                    on_error=self.on_error,
                    on_message=self.on_message
                )

            if token or self.config['port'] == 8002:
                ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
            else:
                ws.run_forever()

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

    def register_receive_callback(self, cls, response):
        self._receive_callbacks += [[cls, response]]

    def on_close(self, _):
        logger.debug('Websocket Connection Closed')
        self.connection = None

    def on_error(self, _, error):
        logger.error(error)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        """Close the connection."""
        if self.connection:
            with self.receive_lock:
                self.connection.close()

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

            logger.info("Sending control command: " + key)
            self.receive_event.clear()
            self.connection.send(payload)
            self.receive_event.wait(0.35)

    _key_interval = 0.5

    def on_message(self, _, message):
        response = json.loads(message)
        logger.debug('incoming message: ' + message)

        if response["event"] == "ms.channel.connect":
            if 'data' in response and 'token' in response["data"]:
                token = self.config['host'] + ':' + response['data']["token"]
                with open(self.token_file, "r") as token_file:
                    token_data = token_file.read().split('\n')

                for line in token_data[:]:
                    if self.config['host'] in line:
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

        for cls, pattern in self._receive_callbacks[:]:
            if pattern == response['event']:
                try:
                    getattr(cls, pattern.split('.')[-1])()
                except AttributeError:
                    logger.error(
                        'Unable to locate remote response callback method %s',
                        pattern.split('.')[-1]
                    )
                self._receive_callbacks.remove([cls, pattern])

    @staticmethod
    def _serialize_string(string):
        if isinstance(string, str):
            string = str.encode(string)

        return base64.b64encode(string).decode("utf-8")

    @property
    def mouse(self):
        return Mouse(self)


class Mouse(object):

    def __init__(self, remote):
        self._remote = remote
        self._is_running = False
        self._commands = []
        self._ime_start_event = threading.Event()
        self._ime_update_event = threading.Event()
        self._touch_enable_event = threading.Event()
        self._send_event = threading.Event()

    @property
    def is_running(self):
        return self._is_running

    def clear(self):
        if not self.is_running:
            del self._commands[:]

    def _send(self, cmd, **kwargs):
        """Send a control command."""

        if not self._remote.connection:
            raise exceptions.ConnectionClosed()

        if not self.is_running:
            params = {
                "Cmd":          cmd,
                "TypeOfRemote": "ProcessMouseDevice"
            }
            params.update(kwargs)

            payload = json.dumps({
                "method": "ms.remote.control",
                "params": params
            })

            self._commands += [payload]

    def left_click(self):
        self._send('LeftClick')

    def right_click(self):
        self._send('RightClick')

    def move(self, x, y):
        position = dict(
            x=x,
            y=y,
            Time=str(time.time())
        )

        self._send('Move', Position=position)

    def add_wait(self, wait):
        if self._is_running:
            self._commands += [wait]

    def imeStart(self):
        self._ime_start_event.set()

    def imeUpdate(self):
        self._ime_update_event.set()

    def touchEnable(self):
        self._touch_enable_event.set()

    def stop(self):
        if self.is_running:
            self._send_event.set()
            self._ime_start_event.set()
            self._ime_update_event.set()
            self._touch_enable_event.set()

    def run(self):
        if not self.is_running:
            self._send_event.clear()
            self._ime_start_event.clear()
            self._ime_update_event.clear()
            self._touch_enable_event.clear()

            self._is_running = True

            with self._remote.receive_lock:
                self._remote.register_receive_callback(
                    self,
                    "ms.remote.imeStart"
                )
                self._remote.register_receive_callback(
                    self,
                    "ms.remote.imeUpdate"
                )
                self._remote.register_receive_callback(
                    self,
                    "ms.remote.touchEnable"
                )

                for payload in self._commands:
                    if isinstance(payload, (float, int)):
                        self._send_event.wait(payload)
                        if self._send_event.isSet():
                            self._is_running = False
                            return
                    else:
                        logger.info(
                            "Sending mouse control command: " + str(payload)
                        )
                        self._remote.receive_event.clear()
                        self._remote.connection.send(payload)

                self._ime_start_event.wait(len(self._commands))
                self._ime_update_event.wait(len(self._commands))
                self._touch_enable_event.wait(len(self._commands))

                self._is_running = False
