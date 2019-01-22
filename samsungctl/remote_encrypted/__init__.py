# -*- coding: utf-8 -*-
"""
The code for the encrypted websocket connection is a modified version of the
SmartCrypto library that was modified by eclair4151.
I want to thank eclair4151 for writing the code that allows the samsungctl
library to support H and J (2014, 2015) model TV's

https://github.com/eclair4151/SmartCrypto
"""

# TODO: Python 2 compatibility

from __future__ import print_function
import sys

if sys.version_info[0] < 3:
    raise ImportError

from . import crypto # NOQA
import re # NOQA
from .command_encryption import AESCipher # NOQA
import requests # NOQA
import time # NOQA
import websocket # NOQA
import logging # NOQA

logger = logging.getLogger('samsungctl')


class RemoteEncrypted(object):

    def __init__(self, config):
        if 'ctx' in config and config['ctx']:
            self.ctx = config['ctx']
        else:
            self.ctx = None

        if 'session_id' in config and config['session_id']:
            try:
                self.current_session_id = int(config['session_id'])
            except ValueError:
                self.current_session_id = config['session_id']
        else:
            self.current_session_id = None

        self.sk_prime = False
        self.last_request_id = 0

        self.user_id = "654321"
        self.AppId = "12345"
        self.device_id = "7e509404-9d7c-46b4-8f6a-e2a9668ad184"
        self.ip = config['host']
        self.port = "8080"
        self.aes_lib = None
        self.connection = None
        self.config = config

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def open(self):
        if self.ctx is None:
            self.start_pairing()
            while self.ctx is None:
                tv_pin = input("Please enter pin from tv: ")

                logger.info("Got pin: '" + tv_pin + "'\n")

                self.first_step_of_pairing()
                output = self.hello_exchange(tv_pin)
                if output:

                    self.ctx = output['ctx'].hex()
                    self.sk_prime = output['sk_prime']
                    logger.debug("ctx: " + self.ctx)
                    logger.info("Pin accepted :)\n")
                else:
                    logger.info("Pin incorrect. Please try again...\n")

            self.current_session_id = self.acknowledge_exchange()
            self.config['session_id'] = self.current_session_id
            self.config['ctx'] = self.ctx

            logger.info('***************************************')
            logger.info('USE THE FOLLOWING NEXT TIME YOU CONNECT')
            logger.info('***************************************')
            logger.info(
                '--host {0} '
                '--method encryption '
                '--session-id {1} '
                '--ctx {2}'.format(self.ip, self.current_session_id, self.ctx)
            )

            self.close_pin_page()
            logger.info("Authorization successful :)\n")

        millis = int(round(time.time() * 1000))
        step4_url = (
            'http://' +
            self.ip +
            ':8000/socket.io/1/?t=' +
            str(millis)
        )

        websocket_response = requests.get(step4_url)
        websocket_url = (
            'ws://' +
            self.ip +
            ':8000/socket.io/1/websocket/' +
            websocket_response.text.split(':')[0]
        )

        logger.debug(websocket_url)

        self.aes_lib = AESCipher(self.ctx.upper(), self.current_session_id)
        self.connection = websocket.create_connection(websocket_url)
        time.sleep(0.35)

    def get_full_url(self, url_path):
        return "http://" + self.ip + ":" + self.port + url_path

    def get_request_url(self, step, app_id, device_id):
        return self.get_full_url(
            "/ws/pairing?step=" +
            str(step) +
            "&app_id=" +
            app_id +
            "&device_id=" +
            device_id
        )

    def show_pin_page(self):
        requests.post(self.get_full_url("/ws/apps/CloudPINPage"), "pin4")

    def check_pin_page(self):
        full_url = self.get_full_url("/ws/apps/CloudPINPage")
        page = requests.get(full_url).text
        output = re.search('state>([^<>]*)</state>', page, flags=re.IGNORECASE)
        if output is not None:
            state = output.group(1)
            logger.debug("Current state: " + state)
            if state == "stopped":
                return True
        return False

    def first_step_of_pairing(self):
        first_step_url = self.get_request_url(0, self.AppId, self.device_id)
        first_step_url += "&type=1"
        _ = requests.get(first_step_url).text

    def start_pairing(self):
        self.last_request_id = 0

        if self.check_pin_page():
            logger.debug("Pin NOT on TV")
            self.show_pin_page()
        else:
            logger.debug("Pin ON TV")

    def hello_exchange(self, pin):
        hello_output = crypto.generateServerHello(self.user_id, pin)

        if not hello_output:
            raise RuntimeError('Connection Failure: hello_exchange 1')

        content = (
            "{\"auth_Data\":{\"auth_type\":\"SPC\",\"GeneratorServerHello\":\""
            + hello_output['serverHello'].hex().upper()
            + "\"}}"
        )

        second_step_url = self.get_request_url(1, self.AppId, self.device_id)
        second_step_response = requests.post(second_step_url, content).text

        logger.debug('second_step_response: ' + second_step_response)

        output = re.search(
            'request_id.*?(\d).*?GeneratorClientHello.*?:.*?(\d[0-9a-zA-Z]*)',
            second_step_response,
            flags=re.IGNORECASE
        )

        if output is None:
            raise RuntimeError('Connection Failure: hello_exchange 2')

        request_id = output.group(1)
        client_hello = output.group(2)
        self.last_request_id = int(request_id)

        return crypto.parseClientHello(
            client_hello,
            hello_output['hash'],
            hello_output['AES_key'],
            self.user_id
        )

    def acknowledge_exchange(self):
        server_ack_message = crypto.generateServerAcknowledge(self.sk_prime)
        content = (
            "{\"auth_Data\":{\"auth_type\":\"SPC\",\"request_id\":\"" +
            str(self.last_request_id) +
            "\",\"ServerAckMsg\":\"" +
            server_ack_message +
            "\"}}"
        )

        third_step_url = self.get_request_url(2, self.AppId, self.device_id)
        third_step_response = requests.post(third_step_url, content).text

        if "secure-mode" in third_step_response:
            raise RuntimeError(
                "TODO: Implement handling of encryption flag!!!!"
            )

        output = re.search(
            'ClientAckMsg.*?:.*?(\d[0-9a-zA-Z]*).*?session_id.*?(\d)',
            third_step_response,
            flags=re.IGNORECASE
        )

        if output is None:
            raise RuntimeError(
                "Unable to get session_id and/or ClientAckMsg!!!"
            )

        client_ack = output.group(1)
        if not crypto.parseClientAcknowledge(client_ack, self.sk_prime):
            raise RuntimeError("Parse client ack message failed.")

        session_id = output.group(2)
        logger.debug("session_id: " + session_id)

        return session_id

    def close_pin_page(self):
        full_url = self.get_full_url("/ws/apps/CloudPINPage/run")
        requests.delete(full_url)
        return False

    def control(self, key):
        if self.connection is None:
            self.open()

        # need sleeps cuz if you send commands to quick it fails
        self.connection.send('1::/com.samsung.companion')
        # pairs to this app with this command.
        time.sleep(0.35)

        self.connection.send(self.aes_lib.generate_command(key))
        time.sleep(0.35)
