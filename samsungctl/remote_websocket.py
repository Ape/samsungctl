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
from . import application


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
        self._registered_callbacks = []

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

    def send(self, method, **params):
        with self.receive_lock:
            payload = dict(
                method=method,
                params=params
            )
            self.receive_event.clear()
            self.connection.send(json.dumps(payload))

    def control(self, key):
        """Send a control command."""
        if not self.connection:
            raise exceptions.ConnectionClosed()

        params = dict(
            Cmd="Click",
            DataOfCmd=key,
            Option="false",
            TypeOfRemote="SendRemoteKey"
        )

        self.send("ms.remote.control", **params)
        self.receive_event.wait(0.35)

    _key_interval = 0.5

    def get_application(self, pattern):
        for app in self.applications:
            if pattern in (app.app_id, app.name):
                return app

    @property
    def applications(self):
        eden_event = threading.Event()
        installed_event = threading.Event()

        app_data = [[], []]

        def eden_app_get(data):
            if 'data' in data:
                app_data[0] = data['data']['data']
            eden_event.set()

        def installed_app_get(data):
            if 'data' in data:
                app_data[1] = data['data']
            installed_event.set()

        self.register_receive_callback(eden_app_get, 'event', 'ed.edenApp.get')
        self.register_receive_callback(installed_app_get, 'data', None)

        for event in ['ed.edenApp.get', 'ed.installedApp.get']:

            params = dict(
                data='',
                event=event,
                to='host'
            )

            self.send('ms.channel.emit', **params)

        eden_event.wait(2.0)
        installed_event.wait(2.0)

        for app_1 in app_data[1]:
            for app_2 in app_data[0]:
                if app_1['appId'] == app_2['appId']:
                    app_1.update(app_2)

        res = []
        for app in app_data[1]:
            res += [application.Application(self, **app)]

        return res

    def register_receive_callback(self, callback, key, data):
        self._registered_callbacks += [[callback, key, data]]

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

        for callback, key, data in self._registered_callbacks[:]:
            if key in response and (data is None or response[key] == data):
                callback(response)
                self._registered_callbacks.remove([callback, key, data])

    @staticmethod
    def _serialize_string(string):
        if isinstance(string, str):
            string = str.encode(string)

        return base64.b64encode(string).decode("utf-8")
