from __future__ import print_function
from . import crypto
import sys
import re
from .command_encryption import AESCipher
import requests
import time
import websocket


class RemoteEncrypted(object):

    def __init__(self, config):
        self.StartPairing()
        if 'ctx' in config and config['ctx']:
            self.ctx = config['ctx']
        else:
            self.ctx = None

        if 'session_id' in config and config['session_id']:
            try:
                self.currentSessionId = int(config['session_id'])
            except ValueError:
                self.currentSessionId = config['session_id']
        else:
            self.currentSessionId = None

        self.SKPrime = False
        self.lastRequestId = 0

        self.UserId = "654321"
        self.AppId = "12345"
        self.deviceId = "7e509404-9d7c-46b4-8f6a-e2a9668ad184"
        self.tvIP = config['host']
        self.tvPort = "8080"
        self.aesLib = None
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

            while self.ctx is None:
                tvPIN = input("Please enter pin from tv: ")

                print("Got pin: '" + tvPIN + "'\n")

                self.FirstStepOfPairing()
                output = self.HelloExchange(tvPIN)
                if output:

                    self.ctx = output['ctx'].hex()
                    self.SKPrime = output['SKPrime']
                    print("ctx: " + self.ctx)
                    print("Pin accepted :)\n")
                else:
                    print("Pin incorrect. Please try again...\n")

            self.currentSessionId = self.AcknowledgeExchange()
            self.config['session_id'] = self.currentSessionId
            self.config['ctx'] = self.ctx

            print('***************************************')
            print('USE THE FOLLOWING NEXT TIME YOU CONNECT')
            print('***************************************')
            print(
                '--host {0} --method encryption --session-id {1} --ctx {2}'.format(
                    self.tvIP,
                    self.currentSessionId,
                    self.ctx
                )
            )

            self.ClosePinPageOnTv()
            print("Authorization successfull :)\n")

        millis = int(round(time.time() * 1000))
        step4_url = (
            'http://' +
            self.tvIP +
            ':8000/socket.io/1/?t=' +
            str(millis)
        )

        websocket_response = requests.get(step4_url)
        websocket_url = (
            'ws://' +
            self.tvIP +
            ':8000/socket.io/1/websocket/' +
            websocket_response.text.split(':')[0]
        )

        print(websocket_url)

        self.aesLib = AESCipher(self.ctx.upper(), self.currentSessionId)
        self.connection = websocket.create_connection(websocket_url)
        time.sleep(0.35)

    def getFullUrl(self, urlPath):
        return "http://" + self.tvIP + ":" + self.tvPort + urlPath

    def GetFullRequestUri(self, step, appId, deviceId):
        return self.getFullUrl(
            "/ws/pairing?step=" +
            str(step) +
            "&app_id=" +
            appId +
            "&device_id=" +
            deviceId
        )

    def ShowPinPageOnTv(self):
        requests.post(self.getFullUrl("/ws/apps/CloudPINPage"), "pin4")

    def CheckPinPageOnTv(self):
        full_url = self.getFullUrl("/ws/apps/CloudPINPage")
        page = requests.get(full_url).text
        output = re.search('state>([^<>]*)</state>', page, flags=re.IGNORECASE)
        if output is not None:
            state = output.group(1)
            print("Current state: " + state)
            if state == "stopped":
                return True
        return False

    def FirstStepOfPairing(self):
        firstStepURL = self.GetFullRequestUri(0, self.AppId, self.deviceId)
        firstStepURL += "&type=1"
        _ = requests.get(firstStepURL).text

    def StartPairing(self):
        self.lastRequestId = 0

        if self.CheckPinPageOnTv():
            print("Pin NOT on TV")
            self.ShowPinPageOnTv()
        else:
            print("Pin ON TV")

    def HelloExchange(self, pin):
        hello_output = crypto.generateServerHello(self.UserId, pin)

        if not hello_output:
            raise RuntimeError('Connection Failure: HelloExchange 1')

        content = (
            "{\"auth_Data\":{\"auth_type\":\"SPC\",\"GeneratorServerHello\":\""
            + hello_output['serverHello'].hex().upper()
            + "\"}}"
        )

        secondStepURL = self.GetFullRequestUri(1, self.AppId, self.deviceId)
        secondStepResponse = requests.post(secondStepURL, content).text

        print('secondStepResponse: ' + secondStepResponse)

        output = re.search(
            'request_id.*?(\d).*?GeneratorClientHello.*?:.*?(\d[0-9a-zA-Z]*)',
            secondStepResponse,
            flags=re.IGNORECASE
        )

        if output is None:
            raise RuntimeError('Connection Failure: HelloExchange 2')

        requestId = output.group(1)
        clientHello = output.group(2)
        self.lastRequestId = int(requestId)

        return crypto.parseClientHello(
            clientHello,
            hello_output['hash'],
            hello_output['AES_key'],
            self.UserId
        )

    def AcknowledgeExchange(self):
        serverAckMessage = crypto.generateServerAcknowledge(self.SKPrime)
        content = (
            "{\"auth_Data\":{\"auth_type\":\"SPC\",\"request_id\":\"" +
            str(self.lastRequestId) +
            "\",\"ServerAckMsg\":\"" +
            serverAckMessage +
            "\"}}"
        )

        thirdStepURL = self.GetFullRequestUri(2, self.AppId, self.deviceId)
        thirdStepResponse = requests.post(thirdStepURL, content).text

        if "secure-mode" in thirdStepResponse:
            print("TODO: Implement handling of encryption flag!!!!")
            sys.exit(-1)

        output = re.search(
            'ClientAckMsg.*?:.*?(\d[0-9a-zA-Z]*).*?session_id.*?(\d)',
            thirdStepResponse,
            flags=re.IGNORECASE
        )

        if output is None:
            print("Unable to get session_id and/or ClientAckMsg!!!")
            sys.exit(-1)

        clientAck = output.group(1)
        if not crypto.parseClientAcknowledge(clientAck, self.SKPrime):
            print("Parse client ac message failed.")
            sys.exit(-1)

        sessionId = output.group(2)
        print("sessionId: " + sessionId)

        return sessionId

    def ClosePinPageOnTv(self):
        full_url = self.getFullUrl("/ws/apps/CloudPINPage/run")
        requests.delete(full_url)
        return False

    def control(self, key):
        if self.connection is None:
            self.open()

        # need sleeps cuz if you send commands to quick it fails
        self.connection.send('1::/com.samsung.companion')
        # pairs to this app with this command.
        time.sleep(0.35)

        self.connection.send(self.aesLib.generate_command(key))
        time.sleep(0.35)
