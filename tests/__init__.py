# -*- coding: utf-8 -*-
from __future__ import print_function
import threading
import unittest
import sys
import os
import ssl
import base64
import json
import random
import string
import time
import uuid
import logging
import socket

from . import responses

logger = logging.getLogger('samsungctl')
logger.addHandler(logging.NullHandler())
logging.basicConfig(format="%(message)s", level=logging.DEBUG)

URL_FORMAT = "ws://{}:{}/api/v2/channels/samsung.remote.control?name={}"
SSL_URL_FORMAT = "wss://{}:{}/api/v2/channels/samsung.remote.control?name={}"
TOKEN = ''.join(
    random.choice(string.digits + string.ascii_letters) for _ in range(20)
)


APP_NAMES = list(
    app['name'] for app in responses.INSTALLED_APP_RESPONSE['data']['data']
)
APP_IDS = list(
    app['appId'] for app in responses.INSTALLED_APP_RESPONSE['data']['data']
)

APP_NAMES += list(
    app['name'] for app in responses.EDEN_APP_RESPONSE['data']['data']
    if app['name'] not in APP_NAMES
)
APP_IDS += list(
    app['id'] for app in responses.EDEN_APP_RESPONSE['data']['data']
    if app['id'] not in APP_IDS
)


def key_wrapper(func):
    key = func.__name__.split('_', 2)[-1]

    def wrapper(self):
        if self.remote is None:
            self.skipTest('no connection')

        event = threading.Event()

        def on_message(message):
            expected_message = dict(
                method='ms.remote.control',
                params=dict(
                    Cmd='Click',
                    DataOfCmd=key,
                    Option="false",
                    TypeOfRemote="SendRemoteKey"
                )
            )
            self.assertEqual(expected_message, message)
            event.set()

        self.client.on_message = on_message

        self.remote.control(key)
        event.wait(1)

        if not event.isSet():
            self.skipTest('timed out')

        self.client.on_message = None

    return wrapper


class FakeWebsocketClient(object):
    def __init__(self, handler):

        self.url = None
        self.sslopt = None
        self.enable_multithread = None
        self.handler = handler
        self.callback = None
        self.return_data = None
        self.on_connect = None
        self.on_message = None
        self.on_close = None
        self.recv_event = threading.Event()

    def __call__(self, url, sslopt, enable_multithread=False):
        self.url = url
        self.sslopt = sslopt
        if 'token' in url:
            token = url.split('token=')[-1]
        else:
            token = None

        self.return_data = self.on_connect(token)
        self.recv_event.set()
        return self

    def send(self, data):
        if self.on_message is None:
            return
        else:
            self.return_data = self.on_message(json.loads(data))

        if self.return_data is not None:
            self.recv_event.set()

    def recv(self):
        self.recv_event.wait()
        self.recv_event.clear()
        response = json.dumps(self.return_data)
        self.return_data = None
        return response

    def close(self):
        self.on_close()


class WebSocketTest(unittest.TestCase):
    remote = None
    client = None
    applications = []
    config = None

    @staticmethod
    def _unserialize_string(s):
        return base64.b64decode(s).encode("utf-8")

    @staticmethod
    def _serialize_string(s):
        return base64.b64encode(s).decode("utf-8")

    def test_001_CONNECTION(self):
        WebSocketTest.config = dict(
            name="samsungctl",
            description="PC",
            id="",
            method="websocket",
            host='127.0.0.1',
            port=8001,
            timeout=0
        )

        self.connection_event = threading.Event()
        WebSocketTest.client = FakeWebsocketClient(self)

        remote_websocket = sys.modules['samsungctl.remote_websocket']
        remote_websocket.websocket.create_connection = self.client

        self.client.on_connect = self.on_connect
        self.client.on_close = self.on_disconnect

        logger.info('connection test')
        logger.info(str(self.config))

        try:
            self.remote = WebSocketTest.remote = samsungctl.Remote(
                self.config,
                logging.DEBUG
            ).__enter__()

            self.remote.open()
            self.connection_event.wait(2)
            if not self.connection_event.isSet():
                WebSocketTest.remote = None
                self.fail('connection timed out')
            else:
                logger.info('connection successful')
        except:
            WebSocketTest.remote = None
            self.fail('unable to establish connection')

    def test_002_CONNECTION_PARAMS(self):
        if self.remote is None:
            self.skipTest('no connection')

        url = URL_FORMAT.format(
            self.config['host'],
            self.config['port'],
            self._serialize_string(self.config['name'])
        )

        self.assertEqual(url, self.client.url)

    # @key_wrapper
    def test_0100_KEY_POWEROFF(self):
        """Power OFF key test"""
        pass

    # @key_wrapper
    def test_0101_KEY_POWERON(self):
        """Power On key test"""
        pass

    # @key_wrapper
    def test_0102_KEY_POWER(self):
        """Power Toggle key test"""
        pass

    @key_wrapper
    def test_0103_KEY_SOURCE(self):
        """Source key test"""
        pass

    @key_wrapper
    def test_0104_KEY_COMPONENT1(self):
        """Component 1 key test"""
        pass

    @key_wrapper
    def test_0105_KEY_COMPONENT2(self):
        """Component 2 key test"""
        pass

    @key_wrapper
    def test_0106_KEY_AV1(self):
        """AV 1 key test"""
        pass

    @key_wrapper
    def test_0107_KEY_AV2(self):
        """AV 2 key test"""
        pass

    @key_wrapper
    def test_0108_KEY_AV3(self):
        """AV 3 key test"""
        pass

    @key_wrapper
    def test_0109_KEY_SVIDEO1(self):
        """S Video 1 key test"""
        pass

    @key_wrapper
    def test_0110_KEY_SVIDEO2(self):
        """S Video 2 key test"""
        pass

    @key_wrapper
    def test_0111_KEY_SVIDEO3(self):
        """S Video 3 key test"""
        pass

    @key_wrapper
    def test_0112_KEY_HDMI(self):
        """HDMI key test"""
        pass

    @key_wrapper
    def test_0113_KEY_HDMI1(self):
        """HDMI 1 key test"""
        pass

    @key_wrapper
    def test_0114_KEY_HDMI2(self):
        """HDMI 2 key test"""
        pass

    @key_wrapper
    def test_0115_KEY_HDMI3(self):
        """HDMI 3 key test"""
        pass

    @key_wrapper
    def test_0116_KEY_HDMI4(self):
        """HDMI 4 key test"""
        pass

    @key_wrapper
    def test_0117_KEY_FM_RADIO(self):
        """FM Radio key test"""
        pass

    @key_wrapper
    def test_0118_KEY_DVI(self):
        """DVI key test"""
        pass

    @key_wrapper
    def test_0119_KEY_DVR(self):
        """DVR key test"""
        pass

    @key_wrapper
    def test_0120_KEY_TV(self):
        """TV key test"""
        pass

    @key_wrapper
    def test_0121_KEY_ANTENA(self):
        """Analog TV key test"""
        pass

    @key_wrapper
    def test_0122_KEY_DTV(self):
        """Digital TV key test"""
        pass

    @key_wrapper
    def test_0123_KEY_1(self):
        """Key1 key test"""
        pass

    @key_wrapper
    def test_0124_KEY_2(self):
        """Key2 key test"""
        pass

    @key_wrapper
    def test_0125_KEY_3(self):
        """Key3 key test"""
        pass

    @key_wrapper
    def test_0126_KEY_4(self):
        """Key4 key test"""
        pass

    @key_wrapper
    def test_0127_KEY_5(self):
        """Key5 key test"""
        pass

    @key_wrapper
    def test_0128_KEY_6(self):
        """Key6 key test"""
        pass

    @key_wrapper
    def test_0129_KEY_7(self):
        """Key7 key test"""
        pass

    @key_wrapper
    def test_0130_KEY_8(self):
        """Key8 key test"""
        pass

    @key_wrapper
    def test_0131_KEY_9(self):
        """Key9 key test"""
        pass

    @key_wrapper
    def test_0132_KEY_0(self):
        """Key0 key test"""
        pass

    @key_wrapper
    def test_0133_KEY_PANNEL_CHDOWN(self):
        """3D key test"""
        pass

    @key_wrapper
    def test_0134_KEY_ANYNET(self):
        """AnyNet+ key test"""
        pass

    @key_wrapper
    def test_0135_KEY_ESAVING(self):
        """Energy Saving key test"""
        pass

    @key_wrapper
    def test_0136_KEY_SLEEP(self):
        """Sleep Timer key test"""
        pass

    @key_wrapper
    def test_0137_KEY_DTV_SIGNAL(self):
        """DTV Signal key test"""
        pass

    @key_wrapper
    def test_0138_KEY_CHUP(self):
        """Channel Up key test"""
        pass

    @key_wrapper
    def test_0139_KEY_CHDOWN(self):
        """Channel Down key test"""
        pass

    @key_wrapper
    def test_0140_KEY_PRECH(self):
        """Previous Channel key test"""
        pass

    @key_wrapper
    def test_0141_KEY_FAVCH(self):
        """Favorite Channels key test"""
        pass

    @key_wrapper
    def test_0142_KEY_CH_LIST(self):
        """Channel List key test"""
        pass

    @key_wrapper
    def test_0143_KEY_AUTO_PROGRAM(self):
        """Auto Program key test"""
        pass

    @key_wrapper
    def test_0144_KEY_MAGIC_CHANNEL(self):
        """Magic Channel key test"""
        pass

    @key_wrapper
    def test_0145_KEY_VOLUP(self):
        """Volume Up key test"""
        pass

    @key_wrapper
    def test_0146_KEY_VOLDOWN(self):
        """Volume Down key test"""
        pass

    @key_wrapper
    def test_0147_KEY_MUTE(self):
        """Mute key test"""
        pass

    @key_wrapper
    def test_0148_KEY_UP(self):
        """Navigation Up key test"""
        pass

    @key_wrapper
    def test_0149_KEY_DOWN(self):
        """Navigation Down key test"""
        pass

    @key_wrapper
    def test_0150_KEY_LEFT(self):
        """Navigation Left key test"""
        pass

    @key_wrapper
    def test_0151_KEY_RIGHT(self):
        """Navigation Right key test"""
        pass

    @key_wrapper
    def test_0152_KEY_RETURN(self):
        """Navigation Return/Back key test"""
        pass

    @key_wrapper
    def test_0153_KEY_ENTER(self):
        """Navigation Enter key test"""
        pass

    @key_wrapper
    def test_0154_KEY_REWIND(self):
        """Rewind key test"""
        pass

    @key_wrapper
    def test_0155_KEY_STOP(self):
        """Stop key test"""
        pass

    @key_wrapper
    def test_0156_KEY_PLAY(self):
        """Play key test"""
        pass

    @key_wrapper
    def test_0157_KEY_FF(self):
        """Fast Forward key test"""
        pass

    @key_wrapper
    def test_0158_KEY_REC(self):
        """Record key test"""
        pass

    @key_wrapper
    def test_0159_KEY_PAUSE(self):
        """Pause key test"""
        pass

    @key_wrapper
    def test_0160_KEY_LIVE(self):
        """Live key test"""
        pass

    @key_wrapper
    def test_0161_KEY_QUICK_REPLAY(self):
        """fnKEY_QUICK_REPLAY key test"""
        pass

    @key_wrapper
    def test_0162_KEY_STILL_PICTURE(self):
        """fnKEY_STILL_PICTURE key test"""
        pass

    @key_wrapper
    def test_0163_KEY_INSTANT_REPLAY(self):
        """fnKEY_INSTANT_REPLAY key test"""
        pass

    @key_wrapper
    def test_0164_KEY_PIP_ONOFF(self):
        """PIP On/Off key test"""
        pass

    @key_wrapper
    def test_0165_KEY_PIP_SWAP(self):
        """PIP Swap key test"""
        pass

    @key_wrapper
    def test_0166_KEY_PIP_SIZE(self):
        """PIP Size key test"""
        pass

    @key_wrapper
    def test_0167_KEY_PIP_CHUP(self):
        """PIP Channel Up key test"""
        pass

    @key_wrapper
    def test_0168_KEY_PIP_CHDOWN(self):
        """PIP Channel Down key test"""
        pass

    @key_wrapper
    def test_0169_KEY_AUTO_ARC_PIP_SMALL(self):
        """PIP Small key test"""
        pass

    @key_wrapper
    def test_0170_KEY_AUTO_ARC_PIP_WIDE(self):
        """PIP Wide key test"""
        pass

    @key_wrapper
    def test_0171_KEY_AUTO_ARC_PIP_RIGHT_BOTTOM(self):
        """PIP Bottom Right key test"""
        pass

    @key_wrapper
    def test_0172_KEY_AUTO_ARC_PIP_SOURCE_CHANGE(self):
        """PIP Source Change key test"""
        pass

    @key_wrapper
    def test_0173_KEY_PIP_SCAN(self):
        """PIP Scan key test"""
        pass

    @key_wrapper
    def test_0174_KEY_VCR_MODE(self):
        """VCR Mode key test"""
        pass

    @key_wrapper
    def test_0175_KEY_CATV_MODE(self):
        """CATV Mode key test"""
        pass

    @key_wrapper
    def test_0176_KEY_DSS_MODE(self):
        """DSS Mode key test"""
        pass

    @key_wrapper
    def test_0177_KEY_TV_MODE(self):
        """TV Mode key test"""
        pass

    @key_wrapper
    def test_0178_KEY_DVD_MODE(self):
        """DVD Mode key test"""
        pass

    @key_wrapper
    def test_0179_KEY_STB_MODE(self):
        """STB Mode key test"""
        pass

    @key_wrapper
    def test_0180_KEY_PCMODE(self):
        """PC Mode key test"""
        pass

    @key_wrapper
    def test_0181_KEY_GREEN(self):
        """Green key test"""
        pass

    @key_wrapper
    def test_0182_KEY_YELLOW(self):
        """Yellow key test"""
        pass

    @key_wrapper
    def test_0183_KEY_CYAN(self):
        """Cyan key test"""
        pass

    @key_wrapper
    def test_0184_KEY_RED(self):
        """Red key test"""
        pass

    @key_wrapper
    def test_0185_KEY_TTX_MIX(self):
        """Teletext Mix key test"""
        pass

    @key_wrapper
    def test_0186_KEY_TTX_SUBFACE(self):
        """Teletext Subface key test"""
        pass

    @key_wrapper
    def test_0187_KEY_ASPECT(self):
        """Aspect Ratio key test"""
        pass

    @key_wrapper
    def test_0188_KEY_PICTURE_SIZE(self):
        """Picture Size key test"""
        pass

    @key_wrapper
    def test_0189_KEY_4_3(self):
        """Aspect Ratio 4:3 key test"""
        pass

    @key_wrapper
    def test_0190_KEY_16_9(self):
        """Aspect Ratio 16:9 key test"""
        pass

    @key_wrapper
    def test_0191_KEY_EXT14(self):
        """Aspect Ratio 3:4 (Alt) key test"""
        pass

    @key_wrapper
    def test_0192_KEY_EXT15(self):
        """Aspect Ratio 16:9 (Alt) key test"""
        pass

    @key_wrapper
    def test_0193_KEY_PMODE(self):
        """Picture Mode key test"""
        pass

    @key_wrapper
    def test_0194_KEY_PANORAMA(self):
        """Picture Mode Panorama key test"""
        pass

    @key_wrapper
    def test_0195_KEY_DYNAMIC(self):
        """Picture Mode Dynamic key test"""
        pass

    @key_wrapper
    def test_0196_KEY_STANDARD(self):
        """Picture Mode Standard key test"""
        pass

    @key_wrapper
    def test_0197_KEY_MOVIE1(self):
        """Picture Mode Movie key test"""
        pass

    @key_wrapper
    def test_0198_KEY_GAME(self):
        """Picture Mode Game key test"""
        pass

    @key_wrapper
    def test_0199_KEY_CUSTOM(self):
        """Picture Mode Custom key test"""
        pass

    @key_wrapper
    def test_0200_KEY_EXT9(self):
        """Picture Mode Movie (Alt) key test"""
        pass

    @key_wrapper
    def test_0201_KEY_EXT10(self):
        """Picture Mode Standard (Alt) key test"""
        pass

    @key_wrapper
    def test_0202_KEY_MENU(self):
        """Menu key test"""
        pass

    @key_wrapper
    def test_0203_KEY_TOPMENU(self):
        """Top Menu key test"""
        pass

    @key_wrapper
    def test_0204_KEY_TOOLS(self):
        """Tools key test"""
        pass

    @key_wrapper
    def test_0205_KEY_HOME(self):
        """Home key test"""
        pass

    @key_wrapper
    def test_0206_KEY_CONTENTS(self):
        """Contents key test"""
        pass

    @key_wrapper
    def test_0207_KEY_GUIDE(self):
        """Guide key test"""
        pass

    @key_wrapper
    def test_0208_KEY_DISC_MENU(self):
        """Disc Menu key test"""
        pass

    @key_wrapper
    def test_0209_KEY_DVR_MENU(self):
        """DVR Menu key test"""
        pass

    @key_wrapper
    def test_0210_KEY_HELP(self):
        """Help key test"""
        pass

    @key_wrapper
    def test_0211_KEY_INFO(self):
        """Info key test"""
        pass

    @key_wrapper
    def test_0212_KEY_CAPTION(self):
        """Caption key test"""
        pass

    @key_wrapper
    def test_0213_KEY_CLOCK_DISPLAY(self):
        """ClockDisplay key test"""
        pass

    @key_wrapper
    def test_0214_KEY_SETUP_CLOCK_TIMER(self):
        """Setup Clock key test"""
        pass

    @key_wrapper
    def test_0215_KEY_SUB_TITLE(self):
        """Subtitle key test"""
        pass

    @key_wrapper
    def test_0216_KEY_ZOOM_MOVE(self):
        """Zoom Move key test"""
        pass

    @key_wrapper
    def test_0217_KEY_ZOOM_IN(self):
        """Zoom In key test"""
        pass

    @key_wrapper
    def test_0218_KEY_ZOOM_OUT(self):
        """Zoom Out key test"""
        pass

    @key_wrapper
    def test_0219_KEY_ZOOM1(self):
        """Zoom 1 key test"""
        pass

    @key_wrapper
    def test_0220_KEY_ZOOM2(self):
        """Zoom 2 key test"""
        pass

    def test_0221_KEY_BT_VOICE_ON(self):
        if self.remote is None:
            self.skipTest('no connection')

        event = threading.Event()

        def on_message(message):
            expected_message = dict(
                method='ms.remote.control',
                params=dict(
                    Cmd='Press',
                    DataOfCmd='KEY_BT_VOICE',
                    Option="false",
                    TypeOfRemote="SendRemoteKey"
                )
            )

            self.assertEqual(expected_message, message)
            payload = dict(event="ms.voiceApp.standby")
            event.set()
            return payload

        self.client.on_message = on_message
        self.remote.start_voice_recognition()

        event.wait(3)
        if not event.isSet():
            self.skipTest('timed out')

        self.client.on_message = None

    def test_0222_KEY_BT_VOICE_OFF(self):
        if self.remote is None:
            self.skipTest('no connection')

        def on_message(message):
            expected_message = dict(
                method='ms.remote.control',
                params=dict(
                    Cmd='Release',
                    DataOfCmd='KEY_BT_VOICE',
                    Option="false",
                    TypeOfRemote="SendRemoteKey"
                )
            )
            self.assertEqual(expected_message, message)
            payload = dict(event="ms.voiceApp.hide")
            event.set()
            return payload

        event = threading.Event()
        self.client.on_message = on_message
        self.remote.stop_voice_recognition()

        event.wait(3)
        if not event.isSet():
            self.skipTest('timed out')

        self.client.on_message = None

    def test_0300_EDEN_APP_GET(self):
        if self.remote is None:
            self.skipTest('no connection')

        def on_message(message):
            eden_message = dict(
                method='ms.channel.emit',
                params=dict(
                    data='',
                    event='ed.edenApp.get',
                    to='host'
                )
            )
            installed_message = dict(
                method='ms.channel.emit',
                params=dict(
                    data='',
                    event='ed.installedApp.get',
                    to='host'
                )
            )

            if message['params']['event'] == 'ed.edenApp.get':
                self.assertEqual(eden_message, message)
                eden_event.set()
                return responses.EDEN_APP_RESPONSE
            elif message['params']['event'] == 'ed.installedApp.get':
                self.assertEqual(installed_message, message)
                installed_event.set()
                return responses.INSTALLED_APP_RESPONSE

        eden_event = threading.Event()
        installed_event = threading.Event()
        application_event = threading.Event()
        self.client.on_message = on_message

        def do():
            try:
                WebSocketTest.applications = self.remote.applications[:]
            except:
                import traceback
                traceback.print_exc()
                self.skipTest('get applications failed')

            application_event.set()

        t = threading.Thread(target=do)
        t.daemon = True
        t.start()

        eden_event.wait(5.0)
        installed_event.wait(5.0)
        if not eden_event.isSet() or not installed_event.isSet():
            self.skipTest('timed out')
        else:
            application_event.wait()

            if not application_event.isSet():
                self.skipTest('no applications received')

            else:
                if not self.applications:
                    self.skipTest('no applications received')

        self.client.on_message = None

    def test_0301_CHECK_APPLICATION_NAMES(self):
        if self.remote is None:
            self.skipTest('no connection')

        if not self.applications:
            self.skipTest('previous test failed')
        else:
            app_names = APP_NAMES[:]
            unknown_names = []

            for app in self.applications:
                if app.name in app_names:
                    app_names.remove(app.name)
                else:
                    unknown_names += [[app.name, app.id]]

            if unknown_names:
                print('unknown apps: ' + str(unknown_names))

            if app_names:
                print('unused apps: ' + str(app_names))

    def test_0302_CHECK_APPLICATION_IDS(self):
        if self.remote is None:
            self.skipTest('no connection')

        if not self.applications:
            self.skipTest('previous test failed')
        else:
            app_ids = APP_IDS[:]
            unknown_ids = []

            for app in self.applications:
                if app.id in app_ids:
                    app_ids.remove(app.id)
                else:
                    unknown_ids += [[app.name, app.id]]

            if unknown_ids:
                print('unknown apps: ' + str(unknown_ids))

            if app_ids:
                print('unused apps: ' + str(app_ids))

    def test_0303_GET_APPLICATION(self):
        if self.remote is None:
            self.skipTest('no connection')

        if not self.applications:
            self.skipTest('previous test failed')
        else:
            def on_message(message):
                eden_message = dict(
                    method='ms.channel.emit',
                    params=dict(
                        data='',
                        event='ed.edenApp.get',
                        to='host'
                    )
                )
                installed_message = dict(
                    method='ms.channel.emit',
                    params=dict(
                        data='',
                        event='ed.installedApp.get',
                        to='host'
                    )
                )

                if message['params']['event'] == 'ed.edenApp.get':
                    self.assertEqual(eden_message, message)
                    eden_event.set()
                    return responses.EDEN_APP_RESPONSE
                elif message['params']['event'] == 'ed.installedApp.get':
                    self.assertEqual(installed_message, message)
                    installed_event.set()
                    return responses.INSTALLED_APP_RESPONSE

            eden_event = threading.Event()
            installed_event = threading.Event()
            application_event = threading.Event()
            self.client.on_message = on_message

            def do():
                try:
                    if self.remote.get_application('Netflix') is None:
                        application_event.set()
                        self.skipTest('get application failed')
                except:
                    import traceback


                    traceback.print_exc()
                    application_event.set()
                    self.skipTest('get application failed')

                application_event.set()

            t = threading.Thread(target=do)
            t.daemon = True
            t.start()

            eden_event.wait(5.0)
            installed_event.wait(5.0)
            if not eden_event.isSet() or not installed_event.isSet():
                self.skipTest('timed out')
            else:
                application_event.wait()

                if not application_event.isSet():
                    self.skipTest('no applications received')

            self.client.on_message = None

    def test_0304_LAUNCH_APPLICATION(self):
        if self.remote is None:
            self.skipTest('no connection')

        if not self.applications:
            self.skipTest('previous test failed')
        else:
            def on_message(message):
                eden_message = dict(
                    method='ms.channel.emit',
                    params=dict(
                        data='',
                        event='ed.edenApp.get',
                        to='host'
                    )
                )
                installed_message = dict(
                    method='ms.channel.emit',
                    params=dict(
                        data='',
                        event='ed.installedApp.get',
                        to='host'
                    )
                )

                if message['params']['event'] == 'ed.edenApp.get':
                    self.assertEqual(eden_message, message)
                    eden_event.set()
                    return responses.EDEN_APP_RESPONSE
                elif message['params']['event'] == 'ed.installedApp.get':
                    self.assertEqual(installed_message, message)
                    installed_event.set()
                    return responses.INSTALLED_APP_RESPONSE

            eden_event = threading.Event()
            installed_event = threading.Event()
            application_event = threading.Event()
            self.client.on_message = on_message

            def do():
                try:
                    app = self.remote.get_application('Netflix')
                    if app is None:
                        application_event.set()
                        self.skipTest('get application failed')
                    else:

                        event = threading.Event()

                        def on_message(message):
                            expected_message = dict(
                                method='ms.channel.emit',
                                params=dict(
                                    event='ed.apps.launch',
                                    to='host',
                                    data=dict(
                                        appId='11101200001',
                                        action_type='DEEP_LINK'
                                    )
                                )
                            )
                            self.assertEqual(expected_message, message)
                            event.set()

                        self.client.on_message = on_message

                        event.wait(2.0)
                        if not event.isSet():
                            self.skipTest('timed out')

                        self.client.on_message = None
                except:
                    import traceback


                    traceback.print_exc()
                    application_event.set()
                    self.skipTest('get application failed')

                application_event.set()

            t = threading.Thread(target=do)
            t.daemon = True
            t.start()

            eden_event.wait(5.0)
            installed_event.wait(5.0)
            if not eden_event.isSet() or not installed_event.isSet():
                self.skipTest('timed out')
            else:
                application_event.wait()

                if not application_event.isSet():
                    self.skipTest('no applications received')

            self.client.on_message = None

    def test_0305_GET_CONTENT_CATEGORY(self):
        if self.remote is None:
            self.skipTest('no connection')

        if not self.applications:
            self.skipTest('previous test failed')
        else:
            def on_message(message):
                eden_message = dict(
                    method='ms.channel.emit',
                    params=dict(
                        data='',
                        event='ed.edenApp.get',
                        to='host'
                    )
                )
                installed_message = dict(
                    method='ms.channel.emit',
                    params=dict(
                        data='',
                        event='ed.installedApp.get',
                        to='host'
                    )
                )

                if message['params']['event'] == 'ed.edenApp.get':
                    self.assertEqual(eden_message, message)
                    eden_event.set()
                    return responses.EDEN_APP_RESPONSE
                elif message['params']['event'] == 'ed.installedApp.get':
                    self.assertEqual(installed_message, message)
                    installed_event.set()
                    return responses.INSTALLED_APP_RESPONSE

            eden_event = threading.Event()
            installed_event = threading.Event()
            application_event = threading.Event()
            self.client.on_message = on_message

            def do():
                try:
                    app = self.remote.get_application('Netflix')

                    if app is None:
                        application_event.set()
                        self.skipTest('get application failed')
                    else:
                        if app.get_category('Trending Now') is None:
                            application_event.set()
                            self.skipTest('get category failed')
                except:
                    import traceback


                    traceback.print_exc()
                    application_event.set()
                    self.skipTest('get application failed')

                application_event.set()

            t = threading.Thread(target=do)
            t.daemon = True
            t.start()

            eden_event.wait(5.0)
            installed_event.wait(5.0)
            if not eden_event.isSet() or not installed_event.isSet():
                self.skipTest('timed out')
            else:
                application_event.wait()

                if not application_event.isSet():
                    self.skipTest('no applications received')

            self.client.on_message = None

    def test_0306_GET_CONTENT(self):
        if self.remote is None:
            self.skipTest('no connection')

        if not self.applications:
            self.skipTest('previous test failed')
        else:
            def on_message(message):
                eden_message = dict(
                    method='ms.channel.emit',
                    params=dict(
                        data='',
                        event='ed.edenApp.get',
                        to='host'
                    )
                )
                installed_message = dict(
                    method='ms.channel.emit',
                    params=dict(
                        data='',
                        event='ed.installedApp.get',
                        to='host'
                    )
                )

                if message['params']['event'] == 'ed.edenApp.get':
                    self.assertEqual(eden_message, message)
                    eden_event.set()
                    return responses.EDEN_APP_RESPONSE
                elif message['params']['event'] == 'ed.installedApp.get':
                    self.assertEqual(installed_message, message)
                    installed_event.set()
                    return responses.INSTALLED_APP_RESPONSE

            eden_event = threading.Event()
            installed_event = threading.Event()
            application_event = threading.Event()
            self.client.on_message = on_message

            def do():
                try:
                    app = self.remote.get_application('Netflix')

                    if app is None:
                        application_event.set()
                        self.skipTest('get application failed')
                    else:
                        category = app.get_category('Trending Now')

                        if category is None:
                            application_event.set()
                            self.skipTest('get category failed')
                        else:
                            if category.get_content(
                                'How the Grinch Stole Christmas') is None:
                                application_event.set()
                                self.skipTest('get content failed')
                except:
                    import traceback


                    traceback.print_exc()
                    application_event.set()
                    self.skipTest('get application failed')

                application_event.set()

            t = threading.Thread(target=do)
            t.daemon = True
            t.start()

            eden_event.wait(5.0)
            installed_event.wait(5.0)
            if not eden_event.isSet() or not installed_event.isSet():
                self.skipTest('timed out')
            else:
                application_event.wait()

                if not application_event.isSet():
                    self.skipTest('no applications received')

            self.client.on_message = None

    def test_0307_PLAY_CONTENT(self):
        if self.remote is None:
            self.skipTest('no connection')

        if not self.applications:
            self.skipTest('previous test failed')
        else:
            def on_message(message):
                eden_message = dict(
                    method='ms.channel.emit',
                    params=dict(
                        data='',
                        event='ed.edenApp.get',
                        to='host'
                    )
                )
                installed_message = dict(
                    method='ms.channel.emit',
                    params=dict(
                        data='',
                        event='ed.installedApp.get',
                        to='host'
                    )
                )

                if message['params']['event'] == 'ed.edenApp.get':
                    self.assertEqual(eden_message, message)
                    eden_event.set()
                    return responses.EDEN_APP_RESPONSE
                elif message['params']['event'] == 'ed.installedApp.get':
                    self.assertEqual(installed_message, message)
                    installed_event.set()
                    return responses.INSTALLED_APP_RESPONSE

            eden_event = threading.Event()
            installed_event = threading.Event()
            application_event = threading.Event()
            self.client.on_message = on_message

            def do():
                try:
                    app = self.remote.get_application('Netflix')

                    if app is None:
                        application_event.set()
                        self.skipTest('get application failed')
                    else:
                        category = app.get_category('Trending Now')

                        if category is None:
                            application_event.set()
                            self.skipTest('get category failed')
                        else:
                            content = category.get_content(
                                'How the Grinch Stole Christmas')
                            if content is None:
                                application_event.set()
                                self.skipTest('get content failed')

                            else:
                                event = threading.Event()

                                def on_message(message):
                                    expected_message = dict(
                                        method='ms.channel.emit',
                                        params=dict(
                                            event='ed.apps.launch',
                                            to='host',
                                            data=dict(
                                                appId='11101200001',
                                                action_type='DEEP_LINK',
                                                metaTag='m=60000901&trackId=254080000&&source_type_payload=groupIndex%3D2%26tileIndex%3D6%26action%3Dmdp%26movieId%3D60000901%26trackId%3D254080000'
                                            )
                                        )
                                    )
                                    self.assertEqual(expected_message, message)
                                    event.set()

                                self.client.on_message = on_message

                                event.wait(2.0)
                                if not event.isSet():
                                    self.skipTest('timed out')

                                self.client.on_message = None
                except:
                    import traceback


                    traceback.print_exc()
                    application_event.set()
                    self.skipTest('get application failed')

                application_event.set()

            t = threading.Thread(target=do)
            t.daemon = True
            t.start()

            eden_event.wait(5.0)
            installed_event.wait(5.0)
            if not eden_event.isSet() or not installed_event.isSet():
                self.skipTest('timed out')
            else:
                application_event.wait()

                if not application_event.isSet():
                    self.skipTest('no applications received')

    def test_999_DISCONNECT(self):
        if self.remote is None:
            self.skipTest('no connection')
        else:
            self.remote.close()

    def on_disconnect(self):
        pass

    def on_connect(self, _):
        guid = str(uuid.uuid4())[1:-1]
        name = self._serialize_string(self.config['name'])

        clients = dict(
            attributes=dict(name=name),
            connectTime=time.time(),
            deviceName=name,
            id=guid,
            isHost=False
        )

        data = dict(clients=[clients], id=guid)
        payload = dict(data=data, event='ms.channel.connect')
        self.connection_event.set()
        return payload


class WebSocketSSLTest(unittest.TestCase):
    remote = None
    client = None
    token = None
    applications = []
    config = None

    @staticmethod
    def _unserialize_string(s):
        return base64.b64decode(s).encode("utf-8")

    @staticmethod
    def _serialize_string(s):
        return base64.b64encode(s).decode("utf-8")

    def test_001_CONNECTION(self):
        WebSocketSSLTest.config = dict(
            name="samsungctl",
            description="PC",
            id="",
            method="websocket",
            host='127.0.0.1',
            port=8002,
            timeout=0
        )
        self.connection_event = threading.Event()
        WebSocketSSLTest.client = FakeWebsocketClient(self)

        remote_websocket = sys.modules['samsungctl.remote_websocket']
        remote_websocket.websocket.create_connection = self.client

        self.client.on_connect = self.on_connect
        self.client.on_close = self.on_disconnect

        logger.info('connection test')
        logger.info(str(self.config))

        try:
            self.remote = WebSocketSSLTest.remote = samsungctl.Remote(
                self.config,
                logging.DEBUG
            ).__enter__()

            self.remote.open()
            self.connection_event.wait(2)
            if not self.connection_event.isSet():
                WebSocketSSLTest.remote = None
                self.fail('connection timed out')
            else:
                logger.info('connection successful')
        except:
            WebSocketSSLTest.remote = None
            self.fail('unable to establish connection')

    def test_002_CONNECTION_PARAMS(self):
        if self.remote is None:
            self.skipTest('no connection')

        url = SSL_URL_FORMAT.format(
            self.config['host'],
            self.config['port'],
            self._serialize_string(self.config['name'])
        )

        sslopt = {"cert_reqs": ssl.CERT_NONE}
        if 'token' in self.client.url:
            url += '&token=' + self.token

        self.assertEqual(url, self.client.url)
        self.assertEqual(sslopt, self.client.sslopt)

    # @key_wrapper
    def test_0100_KEY_POWEROFF(self):
        """Power OFF key test"""
        pass

    # @key_wrapper
    def test_0101_KEY_POWERON(self):
        """Power On key test"""
        pass

    # @key_wrapper
    def test_0102_KEY_POWER(self):
        """Power Toggle key test"""
        pass

    @key_wrapper
    def test_0103_KEY_SOURCE(self):
        """Source key test"""
        pass

    @key_wrapper
    def test_0104_KEY_COMPONENT1(self):
        """Component 1 key test"""
        pass

    @key_wrapper
    def test_0105_KEY_COMPONENT2(self):
        """Component 2 key test"""
        pass

    @key_wrapper
    def test_0106_KEY_AV1(self):
        """AV 1 key test"""
        pass

    @key_wrapper
    def test_0107_KEY_AV2(self):
        """AV 2 key test"""
        pass

    @key_wrapper
    def test_0108_KEY_AV3(self):
        """AV 3 key test"""
        pass

    @key_wrapper
    def test_0109_KEY_SVIDEO1(self):
        """S Video 1 key test"""
        pass

    @key_wrapper
    def test_0110_KEY_SVIDEO2(self):
        """S Video 2 key test"""
        pass

    @key_wrapper
    def test_0111_KEY_SVIDEO3(self):
        """S Video 3 key test"""
        pass

    @key_wrapper
    def test_0112_KEY_HDMI(self):
        """HDMI key test"""
        pass

    @key_wrapper
    def test_0113_KEY_HDMI1(self):
        """HDMI 1 key test"""
        pass

    @key_wrapper
    def test_0114_KEY_HDMI2(self):
        """HDMI 2 key test"""
        pass

    @key_wrapper
    def test_0115_KEY_HDMI3(self):
        """HDMI 3 key test"""
        pass

    @key_wrapper
    def test_0116_KEY_HDMI4(self):
        """HDMI 4 key test"""
        pass

    @key_wrapper
    def test_0117_KEY_FM_RADIO(self):
        """FM Radio key test"""
        pass

    @key_wrapper
    def test_0118_KEY_DVI(self):
        """DVI key test"""
        pass

    @key_wrapper
    def test_0119_KEY_DVR(self):
        """DVR key test"""
        pass

    @key_wrapper
    def test_0120_KEY_TV(self):
        """TV key test"""
        pass

    @key_wrapper
    def test_0121_KEY_ANTENA(self):
        """Analog TV key test"""
        pass

    @key_wrapper
    def test_0122_KEY_DTV(self):
        """Digital TV key test"""
        pass

    @key_wrapper
    def test_0123_KEY_1(self):
        """Key1 key test"""
        pass

    @key_wrapper
    def test_0124_KEY_2(self):
        """Key2 key test"""
        pass

    @key_wrapper
    def test_0125_KEY_3(self):
        """Key3 key test"""
        pass

    @key_wrapper
    def test_0126_KEY_4(self):
        """Key4 key test"""
        pass

    @key_wrapper
    def test_0127_KEY_5(self):
        """Key5 key test"""
        pass

    @key_wrapper
    def test_0128_KEY_6(self):
        """Key6 key test"""
        pass

    @key_wrapper
    def test_0129_KEY_7(self):
        """Key7 key test"""
        pass

    @key_wrapper
    def test_0130_KEY_8(self):
        """Key8 key test"""
        pass

    @key_wrapper
    def test_0131_KEY_9(self):
        """Key9 key test"""
        pass

    @key_wrapper
    def test_0132_KEY_0(self):
        """Key0 key test"""
        pass

    @key_wrapper
    def test_0133_KEY_PANNEL_CHDOWN(self):
        """3D key test"""
        pass

    @key_wrapper
    def test_0134_KEY_ANYNET(self):
        """AnyNet+ key test"""
        pass

    @key_wrapper
    def test_0135_KEY_ESAVING(self):
        """Energy Saving key test"""
        pass

    @key_wrapper
    def test_0136_KEY_SLEEP(self):
        """Sleep Timer key test"""
        pass

    @key_wrapper
    def test_0137_KEY_DTV_SIGNAL(self):
        """DTV Signal key test"""
        pass

    @key_wrapper
    def test_0138_KEY_CHUP(self):
        """Channel Up key test"""
        pass

    @key_wrapper
    def test_0139_KEY_CHDOWN(self):
        """Channel Down key test"""
        pass

    @key_wrapper
    def test_0140_KEY_PRECH(self):
        """Previous Channel key test"""
        pass

    @key_wrapper
    def test_0141_KEY_FAVCH(self):
        """Favorite Channels key test"""
        pass

    @key_wrapper
    def test_0142_KEY_CH_LIST(self):
        """Channel List key test"""
        pass

    @key_wrapper
    def test_0143_KEY_AUTO_PROGRAM(self):
        """Auto Program key test"""
        pass

    @key_wrapper
    def test_0144_KEY_MAGIC_CHANNEL(self):
        """Magic Channel key test"""
        pass

    @key_wrapper
    def test_0145_KEY_VOLUP(self):
        """Volume Up key test"""
        pass

    @key_wrapper
    def test_0146_KEY_VOLDOWN(self):
        """Volume Down key test"""
        pass

    @key_wrapper
    def test_0147_KEY_MUTE(self):
        """Mute key test"""
        pass

    @key_wrapper
    def test_0148_KEY_UP(self):
        """Navigation Up key test"""
        pass

    @key_wrapper
    def test_0149_KEY_DOWN(self):
        """Navigation Down key test"""
        pass

    @key_wrapper
    def test_0150_KEY_LEFT(self):
        """Navigation Left key test"""
        pass

    @key_wrapper
    def test_0151_KEY_RIGHT(self):
        """Navigation Right key test"""
        pass

    @key_wrapper
    def test_0152_KEY_RETURN(self):
        """Navigation Return/Back key test"""
        pass

    @key_wrapper
    def test_0153_KEY_ENTER(self):
        """Navigation Enter key test"""
        pass

    @key_wrapper
    def test_0154_KEY_REWIND(self):
        """Rewind key test"""
        pass

    @key_wrapper
    def test_0155_KEY_STOP(self):
        """Stop key test"""
        pass

    @key_wrapper
    def test_0156_KEY_PLAY(self):
        """Play key test"""
        pass

    @key_wrapper
    def test_0157_KEY_FF(self):
        """Fast Forward key test"""
        pass

    @key_wrapper
    def test_0158_KEY_REC(self):
        """Record key test"""
        pass

    @key_wrapper
    def test_0159_KEY_PAUSE(self):
        """Pause key test"""
        pass

    @key_wrapper
    def test_0160_KEY_LIVE(self):
        """Live key test"""
        pass

    @key_wrapper
    def test_0161_KEY_QUICK_REPLAY(self):
        """fnKEY_QUICK_REPLAY key test"""
        pass

    @key_wrapper
    def test_0162_KEY_STILL_PICTURE(self):
        """fnKEY_STILL_PICTURE key test"""
        pass

    @key_wrapper
    def test_0163_KEY_INSTANT_REPLAY(self):
        """fnKEY_INSTANT_REPLAY key test"""
        pass

    @key_wrapper
    def test_0164_KEY_PIP_ONOFF(self):
        """PIP On/Off key test"""
        pass

    @key_wrapper
    def test_0165_KEY_PIP_SWAP(self):
        """PIP Swap key test"""
        pass

    @key_wrapper
    def test_0166_KEY_PIP_SIZE(self):
        """PIP Size key test"""
        pass

    @key_wrapper
    def test_0167_KEY_PIP_CHUP(self):
        """PIP Channel Up key test"""
        pass

    @key_wrapper
    def test_0168_KEY_PIP_CHDOWN(self):
        """PIP Channel Down key test"""
        pass

    @key_wrapper
    def test_0169_KEY_AUTO_ARC_PIP_SMALL(self):
        """PIP Small key test"""
        pass

    @key_wrapper
    def test_0170_KEY_AUTO_ARC_PIP_WIDE(self):
        """PIP Wide key test"""
        pass

    @key_wrapper
    def test_0171_KEY_AUTO_ARC_PIP_RIGHT_BOTTOM(self):
        """PIP Bottom Right key test"""
        pass

    @key_wrapper
    def test_0172_KEY_AUTO_ARC_PIP_SOURCE_CHANGE(self):
        """PIP Source Change key test"""
        pass

    @key_wrapper
    def test_0173_KEY_PIP_SCAN(self):
        """PIP Scan key test"""
        pass

    @key_wrapper
    def test_0174_KEY_VCR_MODE(self):
        """VCR Mode key test"""
        pass

    @key_wrapper
    def test_0175_KEY_CATV_MODE(self):
        """CATV Mode key test"""
        pass

    @key_wrapper
    def test_0176_KEY_DSS_MODE(self):
        """DSS Mode key test"""
        pass

    @key_wrapper
    def test_0177_KEY_TV_MODE(self):
        """TV Mode key test"""
        pass

    @key_wrapper
    def test_0178_KEY_DVD_MODE(self):
        """DVD Mode key test"""
        pass

    @key_wrapper
    def test_0179_KEY_STB_MODE(self):
        """STB Mode key test"""
        pass

    @key_wrapper
    def test_0180_KEY_PCMODE(self):
        """PC Mode key test"""
        pass

    @key_wrapper
    def test_0181_KEY_GREEN(self):
        """Green key test"""
        pass

    @key_wrapper
    def test_0182_KEY_YELLOW(self):
        """Yellow key test"""
        pass

    @key_wrapper
    def test_0183_KEY_CYAN(self):
        """Cyan key test"""
        pass

    @key_wrapper
    def test_0184_KEY_RED(self):
        """Red key test"""
        pass

    @key_wrapper
    def test_0185_KEY_TTX_MIX(self):
        """Teletext Mix key test"""
        pass

    @key_wrapper
    def test_0186_KEY_TTX_SUBFACE(self):
        """Teletext Subface key test"""
        pass

    @key_wrapper
    def test_0187_KEY_ASPECT(self):
        """Aspect Ratio key test"""
        pass

    @key_wrapper
    def test_0188_KEY_PICTURE_SIZE(self):
        """Picture Size key test"""
        pass

    @key_wrapper
    def test_0189_KEY_4_3(self):
        """Aspect Ratio 4:3 key test"""
        pass

    @key_wrapper
    def test_0190_KEY_16_9(self):
        """Aspect Ratio 16:9 key test"""
        pass

    @key_wrapper
    def test_0191_KEY_EXT14(self):
        """Aspect Ratio 3:4 (Alt) key test"""
        pass

    @key_wrapper
    def test_0192_KEY_EXT15(self):
        """Aspect Ratio 16:9 (Alt) key test"""
        pass

    @key_wrapper
    def test_0193_KEY_PMODE(self):
        """Picture Mode key test"""
        pass

    @key_wrapper
    def test_0194_KEY_PANORAMA(self):
        """Picture Mode Panorama key test"""
        pass

    @key_wrapper
    def test_0195_KEY_DYNAMIC(self):
        """Picture Mode Dynamic key test"""
        pass

    @key_wrapper
    def test_0196_KEY_STANDARD(self):
        """Picture Mode Standard key test"""
        pass

    @key_wrapper
    def test_0197_KEY_MOVIE1(self):
        """Picture Mode Movie key test"""
        pass

    @key_wrapper
    def test_0198_KEY_GAME(self):
        """Picture Mode Game key test"""
        pass

    @key_wrapper
    def test_0199_KEY_CUSTOM(self):
        """Picture Mode Custom key test"""
        pass

    @key_wrapper
    def test_0200_KEY_EXT9(self):
        """Picture Mode Movie (Alt) key test"""
        pass

    @key_wrapper
    def test_0201_KEY_EXT10(self):
        """Picture Mode Standard (Alt) key test"""
        pass

    @key_wrapper
    def test_0202_KEY_MENU(self):
        """Menu key test"""
        pass

    @key_wrapper
    def test_0203_KEY_TOPMENU(self):
        """Top Menu key test"""
        pass

    @key_wrapper
    def test_0204_KEY_TOOLS(self):
        """Tools key test"""
        pass

    @key_wrapper
    def test_0205_KEY_HOME(self):
        """Home key test"""
        pass

    @key_wrapper
    def test_0206_KEY_CONTENTS(self):
        """Contents key test"""
        pass

    @key_wrapper
    def test_0207_KEY_GUIDE(self):
        """Guide key test"""
        pass

    @key_wrapper
    def test_0208_KEY_DISC_MENU(self):
        """Disc Menu key test"""
        pass

    @key_wrapper
    def test_0209_KEY_DVR_MENU(self):
        """DVR Menu key test"""
        pass

    @key_wrapper
    def test_0210_KEY_HELP(self):
        """Help key test"""
        pass

    @key_wrapper
    def test_0211_KEY_INFO(self):
        """Info key test"""
        pass

    @key_wrapper
    def test_0212_KEY_CAPTION(self):
        """Caption key test"""
        pass

    @key_wrapper
    def test_0213_KEY_CLOCK_DISPLAY(self):
        """ClockDisplay key test"""
        pass

    @key_wrapper
    def test_0214_KEY_SETUP_CLOCK_TIMER(self):
        """Setup Clock key test"""
        pass

    @key_wrapper
    def test_0215_KEY_SUB_TITLE(self):
        """Subtitle key test"""
        pass

    @key_wrapper
    def test_0216_KEY_ZOOM_MOVE(self):
        """Zoom Move key test"""
        pass

    @key_wrapper
    def test_0217_KEY_ZOOM_IN(self):
        """Zoom In key test"""
        pass

    @key_wrapper
    def test_0218_KEY_ZOOM_OUT(self):
        """Zoom Out key test"""
        pass

    @key_wrapper
    def test_0219_KEY_ZOOM1(self):
        """Zoom 1 key test"""
        pass

    @key_wrapper
    def test_0220_KEY_ZOOM2(self):
        """Zoom 2 key test"""
        pass

    def test_0221_KEY_BT_VOICE_ON(self):
        if self.remote is None:
            self.skipTest('no connection')

        event = threading.Event()

        def on_message(message):
            expected_message = dict(
                method='ms.remote.control',
                params=dict(
                    Cmd='Press',
                    DataOfCmd='KEY_BT_VOICE',
                    Option="false",
                    TypeOfRemote="SendRemoteKey"
                )
            )

            self.assertEqual(expected_message, message)
            payload = dict(event="ms.voiceApp.standby")
            event.set()
            return payload

        self.client.on_message = on_message
        self.remote.start_voice_recognition()

        event.wait(3)
        if not event.isSet():
            self.skipTest('timed out')

        self.client.on_message = None

    def test_0222_KEY_BT_VOICE_OFF(self):
        if self.remote is None:
            self.skipTest('no connection')

        def on_message(message):
            expected_message = dict(
                method='ms.remote.control',
                params=dict(
                    Cmd='Release',
                    DataOfCmd='KEY_BT_VOICE',
                    Option="false",
                    TypeOfRemote="SendRemoteKey"
                )
            )
            self.assertEqual(expected_message, message)
            payload = dict(event="ms.voiceApp.hide")
            event.set()
            return payload

        event = threading.Event()
        self.client.on_message = on_message
        self.remote.stop_voice_recognition()

        event.wait(3)
        if not event.isSet():
            self.skipTest('timed out')

        self.client.on_message = None

    def test_0300_EDEN_APP_GET(self):
        if self.remote is None:
            self.skipTest('no connection')

        def on_message(message):
            eden_message = dict(
                method='ms.channel.emit',
                params=dict(
                    data='',
                    event='ed.edenApp.get',
                    to='host'
                )
            )
            installed_message = dict(
                method='ms.channel.emit',
                params=dict(
                    data='',
                    event='ed.installedApp.get',
                    to='host'
                )
            )

            if message['params']['event'] == 'ed.edenApp.get':
                self.assertEqual(eden_message, message)
                eden_event.set()
                return responses.EDEN_APP_RESPONSE
            elif message['params']['event'] == 'ed.installedApp.get':
                self.assertEqual(installed_message, message)
                installed_event.set()
                return responses.INSTALLED_APP_RESPONSE

        eden_event = threading.Event()
        installed_event = threading.Event()
        application_event = threading.Event()
        self.client.on_message = on_message

        def do():
            try:
                WebSocketSSLTest.applications = self.remote.applications[:]
            except:
                import traceback
                traceback.print_exc()
                self.skipTest('get applications failed')

            application_event.set()

        t = threading.Thread(target=do)
        t.daemon = True
        t.start()

        eden_event.wait(5.0)
        installed_event.wait(5.0)
        if not eden_event.isSet() or not installed_event.isSet():
            self.skipTest('timed out')
        else:
            application_event.wait()

            if not application_event.isSet():
                self.skipTest('no applications received')

            else:
                if not self.applications:
                    self.skipTest('no applications received')

        self.client.on_message = None

    def test_0301_CHECK_APPLICATION_NAMES(self):
        if self.remote is None:
            self.skipTest('no connection')

        if not self.applications:
            self.skipTest('previous test failed')
        else:
            app_names = APP_NAMES[:]
            unknown_names = []

            for app in self.applications:
                if app.name in app_names:
                    app_names.remove(app.name)
                else:
                    unknown_names += [[app.name, app.id]]

            if unknown_names:
                print('unknown apps: ' + str(unknown_names))

            if app_names:
                print('unused apps: ' + str(app_names))

    def test_0302_CHECK_APPLICATION_IDS(self):
        if self.remote is None:
            self.skipTest('no connection')

        if not self.applications:
            self.skipTest('previous test failed')
        else:
            app_ids = APP_IDS[:]
            unknown_ids = []

            for app in self.applications:
                if app.id in app_ids:
                    app_ids.remove(app.id)
                else:
                    unknown_ids += [[app.name, app.id]]

            if unknown_ids:
                print('unknown apps: ' + str(unknown_ids))

            if app_ids:
                print('unused apps: ' + str(app_ids))

    def test_0303_GET_APPLICATION(self):
        if self.remote is None:
            self.skipTest('no connection')

        if not self.applications:
            self.skipTest('previous test failed')
        else:
            def on_message(message):
                eden_message = dict(
                    method='ms.channel.emit',
                    params=dict(
                        data='',
                        event='ed.edenApp.get',
                        to='host'
                    )
                )
                installed_message = dict(
                    method='ms.channel.emit',
                    params=dict(
                        data='',
                        event='ed.installedApp.get',
                        to='host'
                    )
                )

                if message['params']['event'] == 'ed.edenApp.get':
                    self.assertEqual(eden_message, message)
                    eden_event.set()
                    return responses.EDEN_APP_RESPONSE
                elif message['params']['event'] == 'ed.installedApp.get':
                    self.assertEqual(installed_message, message)
                    installed_event.set()
                    return responses.INSTALLED_APP_RESPONSE

            eden_event = threading.Event()
            installed_event = threading.Event()
            application_event = threading.Event()
            self.client.on_message = on_message

            def do():
                try:
                    if self.remote.get_application('Netflix') is None:
                        application_event.set()
                        self.skipTest('get application failed')
                except:
                    import traceback

                    traceback.print_exc()
                    application_event.set()
                    self.skipTest('get application failed')

                application_event.set()

            t = threading.Thread(target=do)
            t.daemon = True
            t.start()

            eden_event.wait(5.0)
            installed_event.wait(5.0)
            if not eden_event.isSet() or not installed_event.isSet():
                self.skipTest('timed out')
            else:
                application_event.wait()

                if not application_event.isSet():
                    self.skipTest('no applications received')

            self.client.on_message = None

    def test_0304_LAUNCH_APPLICATION(self):
        if self.remote is None:
            self.skipTest('no connection')

        if not self.applications:
            self.skipTest('previous test failed')
        else:
            def on_message(message):
                eden_message = dict(
                    method='ms.channel.emit',
                    params=dict(
                        data='',
                        event='ed.edenApp.get',
                        to='host'
                    )
                )
                installed_message = dict(
                    method='ms.channel.emit',
                    params=dict(
                        data='',
                        event='ed.installedApp.get',
                        to='host'
                    )
                )

                if message['params']['event'] == 'ed.edenApp.get':
                    self.assertEqual(eden_message, message)
                    eden_event.set()
                    return responses.EDEN_APP_RESPONSE
                elif message['params']['event'] == 'ed.installedApp.get':
                    self.assertEqual(installed_message, message)
                    installed_event.set()
                    return responses.INSTALLED_APP_RESPONSE

            eden_event = threading.Event()
            installed_event = threading.Event()
            application_event = threading.Event()
            self.client.on_message = on_message

            def do():
                try:
                    app = self.remote.get_application('Netflix')
                    if app is None:
                        application_event.set()
                        self.skipTest('get application failed')
                    else:

                        event = threading.Event()

                        def on_message(message):
                            expected_message = dict(
                                method='ms.channel.emit',
                                params=dict(
                                    event='ed.apps.launch',
                                    to='host',
                                    data=dict(
                                        appId='11101200001',
                                        action_type='DEEP_LINK'
                                    )
                                )
                            )
                            self.assertEqual(expected_message, message)
                            event.set()

                        self.client.on_message = on_message

                        event.wait(2.0)
                        if not event.isSet():
                            self.skipTest('timed out')

                        self.client.on_message = None
                except:
                    import traceback

                    traceback.print_exc()
                    application_event.set()
                    self.skipTest('get application failed')

                application_event.set()

            t = threading.Thread(target=do)
            t.daemon = True
            t.start()

            eden_event.wait(5.0)
            installed_event.wait(5.0)
            if not eden_event.isSet() or not installed_event.isSet():
                self.skipTest('timed out')
            else:
                application_event.wait()

                if not application_event.isSet():
                    self.skipTest('no applications received')

            self.client.on_message = None

    def test_0305_GET_CONTENT_CATEGORY(self):
        if self.remote is None:
            self.skipTest('no connection')

        if not self.applications:
            self.skipTest('previous test failed')
        else:
            def on_message(message):
                eden_message = dict(
                    method='ms.channel.emit',
                    params=dict(
                        data='',
                        event='ed.edenApp.get',
                        to='host'
                    )
                )
                installed_message = dict(
                    method='ms.channel.emit',
                    params=dict(
                        data='',
                        event='ed.installedApp.get',
                        to='host'
                    )
                )

                if message['params']['event'] == 'ed.edenApp.get':
                    self.assertEqual(eden_message, message)
                    eden_event.set()
                    return responses.EDEN_APP_RESPONSE
                elif message['params']['event'] == 'ed.installedApp.get':
                    self.assertEqual(installed_message, message)
                    installed_event.set()
                    return responses.INSTALLED_APP_RESPONSE

            eden_event = threading.Event()
            installed_event = threading.Event()
            application_event = threading.Event()
            self.client.on_message = on_message

            def do():
                try:
                    app = self.remote.get_application('Netflix')

                    if app is None:
                        application_event.set()
                        self.skipTest('get application failed')
                    else:
                        if app.get_category('Trending Now') is None:
                            application_event.set()
                            self.skipTest('get category failed')
                except:
                    import traceback

                    traceback.print_exc()
                    application_event.set()
                    self.skipTest('get application failed')

                application_event.set()

            t = threading.Thread(target=do)
            t.daemon = True
            t.start()

            eden_event.wait(5.0)
            installed_event.wait(5.0)
            if not eden_event.isSet() or not installed_event.isSet():
                self.skipTest('timed out')
            else:
                application_event.wait()

                if not application_event.isSet():
                    self.skipTest('no applications received')

            self.client.on_message = None

    def test_0306_GET_CONTENT(self):
        if self.remote is None:
            self.skipTest('no connection')

        if not self.applications:
            self.skipTest('previous test failed')
        else:
            def on_message(message):
                eden_message = dict(
                    method='ms.channel.emit',
                    params=dict(
                        data='',
                        event='ed.edenApp.get',
                        to='host'
                    )
                )
                installed_message = dict(
                    method='ms.channel.emit',
                    params=dict(
                        data='',
                        event='ed.installedApp.get',
                        to='host'
                    )
                )

                if message['params']['event'] == 'ed.edenApp.get':
                    self.assertEqual(eden_message, message)
                    eden_event.set()
                    return responses.EDEN_APP_RESPONSE
                elif message['params']['event'] == 'ed.installedApp.get':
                    self.assertEqual(installed_message, message)
                    installed_event.set()
                    return responses.INSTALLED_APP_RESPONSE

            eden_event = threading.Event()
            installed_event = threading.Event()
            application_event = threading.Event()
            self.client.on_message = on_message

            def do():
                try:
                    app = self.remote.get_application('Netflix')

                    if app is None:
                        application_event.set()
                        self.skipTest('get application failed')
                    else:
                        category = app.get_category('Trending Now')

                        if category is None:
                            application_event.set()
                            self.skipTest('get category failed')
                        else:
                            if category.get_content('How the Grinch Stole Christmas') is None:
                                application_event.set()
                                self.skipTest('get content failed')
                except:
                    import traceback

                    traceback.print_exc()
                    application_event.set()
                    self.skipTest('get application failed')

                application_event.set()

            t = threading.Thread(target=do)
            t.daemon = True
            t.start()

            eden_event.wait(5.0)
            installed_event.wait(5.0)
            if not eden_event.isSet() or not installed_event.isSet():
                self.skipTest('timed out')
            else:
                application_event.wait()

                if not application_event.isSet():
                    self.skipTest('no applications received')

            self.client.on_message = None

    def test_0307_PLAY_CONTENT(self):
        if self.remote is None:
            self.skipTest('no connection')

        if not self.applications:
            self.skipTest('previous test failed')
        else:
            def on_message(message):
                eden_message = dict(
                    method='ms.channel.emit',
                    params=dict(
                        data='',
                        event='ed.edenApp.get',
                        to='host'
                    )
                )
                installed_message = dict(
                    method='ms.channel.emit',
                    params=dict(
                        data='',
                        event='ed.installedApp.get',
                        to='host'
                    )
                )

                if message['params']['event'] == 'ed.edenApp.get':
                    self.assertEqual(eden_message, message)
                    eden_event.set()
                    return responses.EDEN_APP_RESPONSE
                elif message['params']['event'] == 'ed.installedApp.get':
                    self.assertEqual(installed_message, message)
                    installed_event.set()
                    return responses.INSTALLED_APP_RESPONSE

            eden_event = threading.Event()
            installed_event = threading.Event()
            application_event = threading.Event()
            self.client.on_message = on_message

            def do():
                try:
                    app = self.remote.get_application('Netflix')

                    if app is None:
                        application_event.set()
                        self.skipTest('get application failed')
                    else:
                        category = app.get_category('Trending Now')

                        if category is None:
                            application_event.set()
                            self.skipTest('get category failed')
                        else:
                            content = category.get_content('How the Grinch Stole Christmas')
                            if content is None:
                                application_event.set()
                                self.skipTest('get content failed')

                            else:
                                event = threading.Event()

                                def on_message(message):
                                    expected_message = dict(
                                        method='ms.channel.emit',
                                        params=dict(
                                            event='ed.apps.launch',
                                            to='host',
                                            data=dict(
                                                appId='11101200001',
                                                action_type='DEEP_LINK',
                                                metaTag='m=60000901&trackId=254080000&&source_type_payload=groupIndex%3D2%26tileIndex%3D6%26action%3Dmdp%26movieId%3D60000901%26trackId%3D254080000'
                                            )
                                        )
                                    )
                                    self.assertEqual(expected_message, message)
                                    event.set()

                                self.client.on_message = on_message

                                event.wait(2.0)
                                if not event.isSet():
                                    self.skipTest('timed out')

                                self.client.on_message = None
                except:
                    import traceback

                    traceback.print_exc()
                    application_event.set()
                    self.skipTest('get application failed')

                application_event.set()

            t = threading.Thread(target=do)
            t.daemon = True
            t.start()

            eden_event.wait(5.0)
            installed_event.wait(5.0)
            if not eden_event.isSet() or not installed_event.isSet():
                self.skipTest('timed out')
            else:
                application_event.wait()

                if not application_event.isSet():
                    self.skipTest('no applications received')

            self.client.on_message = None

    def test_999_DISCONNECT(self):
        if self.remote is None:
            self.skipTest('no connection')
        else:
            self.remote.close()

    def on_disconnect(self):
        pass

    def on_connect(self, token):
        guid = str(uuid.uuid4())[1:-1]
        name = self._serialize_string(self.config['name'])
        if token is None:
            token = TOKEN

        WebSocketSSLTest.token = token
        clients = dict(
            attributes=dict(name=name, token=token),
            connectTime=time.time(),
            deviceName=name,
            id=guid,
            isHost=False
        )

        data = dict(clients=[clients], id=guid, token=token)
        payload = dict(data=data, event='ms.channel.connect')
        self.connection_event.set()
        return payload


class LegacySocket(object):

    def __init__(self, handler):
        self.handler = handler
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('127.0.0.1', 55000))
        self.sock.listen(1)
        self.on_message = None
        self.on_connect = None
        self.on_close = None
        self._event = threading.Event()
        self._thread = threading.Thread(target=self.loop)
        self._thread.start()
        self.conn =  None

    def send(self, message):
        # print(repr(message))
        self.conn.sendall(message)

    def loop(self):
        conn, addr = self.sock.accept()
        self.conn = conn
        data = conn.recv(4096)
        self.on_connect(data)

        try:

            while not self._event.isSet():
                data = conn.recv(4096)
                if self.on_message is not None:
                    self.on_message(data)

        except socket.error:
            pass

    def close(self):
        self.sock.close()


def send_key(func):
    key = func.__name__.split('_', 2)[-1]

    def wrapper(self):
        self.send_command(key)

    return wrapper


class LegacyTest(unittest.TestCase):
    remote = None
    client = None
    token = None
    applications = []
    config = None

    @staticmethod
    def _unserialize_string(s):
        return base64.b64decode(s).encode("utf-8")

    @staticmethod
    def _serialize_string(string, raw=False):
        if isinstance(string, str):
            if sys.version_info[0] > 2:
                string = str.encode(string)

        if not raw:
            string = base64.b64encode(string)

        return bytes([len(string)]) + b"\x00" + string

    def test_001_CONNECTION(self):
        LegacyTest.config = dict(
            name="samsungctl",
            description="UnitTest",
            id="123456789",
            method="legacy",
            host='127.0.0.1',
            port=55000,
            timeout=0
        )

        LegacyTest.client = LegacySocket(self)

        self.connection_event = threading.Event()

        self.client.on_connect = self.on_connect
        self.client.on_close = self.on_disconnect

        logger.info('connection test')
        logger.info(str(self.config))

        try:
            self.remote = LegacyTest.remote = samsungctl.Remote(
                self.config,
                logging.DEBUG
            ).__enter__()

            self.connection_event.wait(2)
            if not self.connection_event.isSet():
                LegacyTest.remote = None
                self.fail('connection timed out')
            else:
                logger.info('connection successful')
        except:
            LegacyTest.remote = None
            self.fail('unable to establish connection')

    def send_command(self, key):

        if self.remote is None:
            self.skipTest('no connection')

        event = threading.Event()

        def on_message(message):
            expected_message = b"\x00\x00\x00" + self._serialize_string(key)
            expected_message = b"\x00\x00\x00" + self._serialize_string(
                expected_message,
                True
            )

            self.assertEqual(expected_message, message)

            tv_name = self.config["name"]
            tv_name_len = bytearray.fromhex(hex(len(tv_name))[2:].zfill(2))

            while len(tv_name_len) < 3:
                tv_name_len = '\x00' + tv_name_len

            packet = tv_name_len + tv_name + b"\x00\x04\x00\x00\x00\x00"

            self.client.send(packet)
            event.set()

        self.client.on_message = on_message

        self.remote.control(key)
        event.wait(1)

        if not event.isSet():
            self.skipTest('timed out')

        self.client.on_message = None

    # @send_key
    def test_0100_KEY_POWEROFF(self):
        """Power OFF key test"""
        pass

    # @send_key
    def test_0101_KEY_POWERON(self):
        """Power On key test"""
        pass

    # @send_key
    def test_0102_KEY_POWER(self):
        """Power Toggle key test"""
        pass

    @send_key
    def test_0103_KEY_SOURCE(self):
        """Source key test"""
        pass

    @send_key
    def test_0104_KEY_COMPONENT1(self):
        """Component 1 key test"""
        pass

    @send_key
    def test_0105_KEY_COMPONENT2(self):
        """Component 2 key test"""
        pass

    @send_key
    def test_0106_KEY_AV1(self):
        """AV 1 key test"""
        pass

    @send_key
    def test_0107_KEY_AV2(self):
        """AV 2 key test"""
        pass

    @send_key
    def test_0108_KEY_AV3(self):
        """AV 3 key test"""
        pass

    @send_key
    def test_0109_KEY_SVIDEO1(self):
        """S Video 1 key test"""
        pass

    @send_key
    def test_0110_KEY_SVIDEO2(self):
        """S Video 2 key test"""
        pass

    @send_key
    def test_0111_KEY_SVIDEO3(self):
        """S Video 3 key test"""
        pass

    @send_key
    def test_0112_KEY_HDMI(self):
        """HDMI key test"""
        pass

    @send_key
    def test_0113_KEY_HDMI1(self):
        """HDMI 1 key test"""
        pass

    @send_key
    def test_0114_KEY_HDMI2(self):
        """HDMI 2 key test"""
        pass

    @send_key
    def test_0115_KEY_HDMI3(self):
        """HDMI 3 key test"""
        pass

    @send_key
    def test_0116_KEY_HDMI4(self):
        """HDMI 4 key test"""
        pass

    @send_key
    def test_0117_KEY_FM_RADIO(self):
        """FM Radio key test"""
        pass

    @send_key
    def test_0118_KEY_DVI(self):
        """DVI key test"""
        pass

    @send_key
    def test_0119_KEY_DVR(self):
        """DVR key test"""
        pass

    @send_key
    def test_0120_KEY_TV(self):
        """TV key test"""
        pass

    @send_key
    def test_0121_KEY_ANTENA(self):
        """Analog TV key test"""
        pass

    @send_key
    def test_0122_KEY_DTV(self):
        """Digital TV key test"""
        pass

    @send_key
    def test_0123_KEY_1(self):
        """Key1 key test"""
        pass

    @send_key
    def test_0124_KEY_2(self):
        """Key2 key test"""
        pass

    @send_key
    def test_0125_KEY_3(self):
        """Key3 key test"""
        pass

    @send_key
    def test_0126_KEY_4(self):
        """Key4 key test"""
        pass

    @send_key
    def test_0127_KEY_5(self):
        """Key5 key test"""
        pass

    @send_key
    def test_0128_KEY_6(self):
        """Key6 key test"""
        pass

    @send_key
    def test_0129_KEY_7(self):
        """Key7 key test"""
        pass

    @send_key
    def test_0130_KEY_8(self):
        """Key8 key test"""
        pass

    @send_key
    def test_0131_KEY_9(self):
        """Key9 key test"""
        pass

    @send_key
    def test_0132_KEY_0(self):
        """Key0 key test"""
        pass

    @send_key
    def test_0133_KEY_PANNEL_CHDOWN(self):
        """3D key test"""
        pass

    @send_key
    def test_0134_KEY_ANYNET(self):
        """AnyNet+ key test"""
        pass

    @send_key
    def test_0135_KEY_ESAVING(self):
        """Energy Saving key test"""
        pass

    @send_key
    def test_0136_KEY_SLEEP(self):
        """Sleep Timer key test"""
        pass

    @send_key
    def test_0137_KEY_DTV_SIGNAL(self):
        """DTV Signal key test"""
        pass

    @send_key
    def test_0138_KEY_CHUP(self):
        """Channel Up key test"""
        pass

    @send_key
    def test_0139_KEY_CHDOWN(self):
        """Channel Down key test"""
        pass

    @send_key
    def test_0140_KEY_PRECH(self):
        """Previous Channel key test"""
        pass

    @send_key
    def test_0141_KEY_FAVCH(self):
        """Favorite Channels key test"""
        pass

    @send_key
    def test_0142_KEY_CH_LIST(self):
        """Channel List key test"""
        pass

    @send_key
    def test_0143_KEY_AUTO_PROGRAM(self):
        """Auto Program key test"""
        pass

    @send_key
    def test_0144_KEY_MAGIC_CHANNEL(self):
        """Magic Channel key test"""
        pass

    @send_key
    def test_0145_KEY_VOLUP(self):
        """Volume Up key test"""
        pass

    @send_key
    def test_0146_KEY_VOLDOWN(self):
        """Volume Down key test"""
        pass

    @send_key
    def test_0147_KEY_MUTE(self):
        """Mute key test"""
        pass

    @send_key
    def test_0148_KEY_UP(self):
        """Navigation Up key test"""
        pass

    @send_key
    def test_0149_KEY_DOWN(self):
        """Navigation Down key test"""
        pass

    @send_key
    def test_0150_KEY_LEFT(self):
        """Navigation Left key test"""
        pass

    @send_key
    def test_0151_KEY_RIGHT(self):
        """Navigation Right key test"""
        pass

    @send_key
    def test_0152_KEY_RETURN(self):
        """Navigation Return/Back key test"""
        pass

    @send_key
    def test_0153_KEY_ENTER(self):
        """Navigation Enter key test"""
        pass

    @send_key
    def test_0154_KEY_REWIND(self):
        """Rewind key test"""
        pass

    @send_key
    def test_0155_KEY_STOP(self):
        """Stop key test"""
        pass

    @send_key
    def test_0156_KEY_PLAY(self):
        """Play key test"""
        pass

    @send_key
    def test_0157_KEY_FF(self):
        """Fast Forward key test"""
        pass

    @send_key
    def test_0158_KEY_REC(self):
        """Record key test"""
        pass

    @send_key
    def test_0159_KEY_PAUSE(self):
        """Pause key test"""
        pass

    @send_key
    def test_0160_KEY_LIVE(self):
        """Live key test"""
        pass

    @send_key
    def test_0161_KEY_QUICK_REPLAY(self):
        """fnKEY_QUICK_REPLAY key test"""
        pass

    @send_key
    def test_0162_KEY_STILL_PICTURE(self):
        """fnKEY_STILL_PICTURE key test"""
        pass

    @send_key
    def test_0163_KEY_INSTANT_REPLAY(self):
        """fnKEY_INSTANT_REPLAY key test"""
        pass

    @send_key
    def test_0164_KEY_PIP_ONOFF(self):
        """PIP On/Off key test"""
        pass

    @send_key
    def test_0165_KEY_PIP_SWAP(self):
        """PIP Swap key test"""
        pass

    @send_key
    def test_0166_KEY_PIP_SIZE(self):
        """PIP Size key test"""
        pass

    @send_key
    def test_0167_KEY_PIP_CHUP(self):
        """PIP Channel Up key test"""
        pass

    @send_key
    def test_0168_KEY_PIP_CHDOWN(self):
        """PIP Channel Down key test"""
        pass

    @send_key
    def test_0169_KEY_AUTO_ARC_PIP_SMALL(self):
        """PIP Small key test"""
        pass

    @send_key
    def test_0170_KEY_AUTO_ARC_PIP_WIDE(self):
        """PIP Wide key test"""
        pass

    @send_key
    def test_0171_KEY_AUTO_ARC_PIP_RIGHT_BOTTOM(self):
        """PIP Bottom Right key test"""
        pass

    @send_key
    def test_0172_KEY_AUTO_ARC_PIP_SOURCE_CHANGE(self):
        """PIP Source Change key test"""
        pass

    @send_key
    def test_0173_KEY_PIP_SCAN(self):
        """PIP Scan key test"""
        pass

    @send_key
    def test_0174_KEY_VCR_MODE(self):
        """VCR Mode key test"""
        pass

    @send_key
    def test_0175_KEY_CATV_MODE(self):
        """CATV Mode key test"""
        pass

    @send_key
    def test_0176_KEY_DSS_MODE(self):
        """DSS Mode key test"""
        pass

    @send_key
    def test_0177_KEY_TV_MODE(self):
        """TV Mode key test"""
        pass

    @send_key
    def test_0178_KEY_DVD_MODE(self):
        """DVD Mode key test"""
        pass

    @send_key
    def test_0179_KEY_STB_MODE(self):
        """STB Mode key test"""
        pass

    @send_key
    def test_0180_KEY_PCMODE(self):
        """PC Mode key test"""
        pass

    @send_key
    def test_0181_KEY_GREEN(self):
        """Green key test"""
        pass

    @send_key
    def test_0182_KEY_YELLOW(self):
        """Yellow key test"""
        pass

    @send_key
    def test_0183_KEY_CYAN(self):
        """Cyan key test"""
        pass

    @send_key
    def test_0184_KEY_RED(self):
        """Red key test"""
        pass

    @send_key
    def test_0185_KEY_TTX_MIX(self):
        """Teletext Mix key test"""
        pass

    @send_key
    def test_0186_KEY_TTX_SUBFACE(self):
        """Teletext Subface key test"""
        pass

    @send_key
    def test_0187_KEY_ASPECT(self):
        """Aspect Ratio key test"""
        pass

    @send_key
    def test_0188_KEY_PICTURE_SIZE(self):
        """Picture Size key test"""
        pass

    @send_key
    def test_0189_KEY_4_3(self):
        """Aspect Ratio 4:3 key test"""
        pass

    @send_key
    def test_0190_KEY_16_9(self):
        """Aspect Ratio 16:9 key test"""
        pass

    @send_key
    def test_0191_KEY_EXT14(self):
        """Aspect Ratio 3:4 (Alt) key test"""
        pass

    @send_key
    def test_0192_KEY_EXT15(self):
        """Aspect Ratio 16:9 (Alt) key test"""
        pass

    @send_key
    def test_0193_KEY_PMODE(self):
        """Picture Mode key test"""
        pass

    @send_key
    def test_0194_KEY_PANORAMA(self):
        """Picture Mode Panorama key test"""
        pass

    @send_key
    def test_0195_KEY_DYNAMIC(self):
        """Picture Mode Dynamic key test"""
        pass

    @send_key
    def test_0196_KEY_STANDARD(self):
        """Picture Mode Standard key test"""
        pass

    @send_key
    def test_0197_KEY_MOVIE1(self):
        """Picture Mode Movie key test"""
        pass

    @send_key
    def test_0198_KEY_GAME(self):
        """Picture Mode Game key test"""
        pass

    @send_key
    def test_0199_KEY_CUSTOM(self):
        """Picture Mode Custom key test"""
        pass

    @send_key
    def test_0200_KEY_EXT9(self):
        """Picture Mode Movie (Alt) key test"""
        pass

    @send_key
    def test_0201_KEY_EXT10(self):
        """Picture Mode Standard (Alt) key test"""
        pass

    @send_key
    def test_0202_KEY_MENU(self):
        """Menu key test"""
        pass

    @send_key
    def test_0203_KEY_TOPMENU(self):
        """Top Menu key test"""
        pass

    @send_key
    def test_0204_KEY_TOOLS(self):
        """Tools key test"""
        pass

    @send_key
    def test_0205_KEY_HOME(self):
        """Home key test"""
        pass

    @send_key
    def test_0206_KEY_CONTENTS(self):
        """Contents key test"""
        pass

    @send_key
    def test_0207_KEY_GUIDE(self):
        """Guide key test"""
        pass

    @send_key
    def test_0208_KEY_DISC_MENU(self):
        """Disc Menu key test"""
        pass

    @send_key
    def test_0209_KEY_DVR_MENU(self):
        """DVR Menu key test"""
        pass

    @send_key
    def test_0210_KEY_HELP(self):
        """Help key test"""
        pass

    @send_key
    def test_0211_KEY_INFO(self):
        """Info key test"""
        pass

    @send_key
    def test_0212_KEY_CAPTION(self):
        """Caption key test"""
        pass

    @send_key
    def test_0213_KEY_CLOCK_DISPLAY(self):
        """ClockDisplay key test"""
        pass

    @send_key
    def test_0214_KEY_SETUP_CLOCK_TIMER(self):
        """Setup Clock key test"""
        pass

    @send_key
    def test_0215_KEY_SUB_TITLE(self):
        """Subtitle key test"""
        pass

    @send_key
    def test_0216_KEY_ZOOM_MOVE(self):
        """Zoom Move key test"""
        pass

    @send_key
    def test_0217_KEY_ZOOM_IN(self):
        """Zoom In key test"""
        pass

    @send_key
    def test_0218_KEY_ZOOM_OUT(self):
        """Zoom Out key test"""
        pass

    @send_key
    def test_0219_KEY_ZOOM1(self):
        """Zoom 1 key test"""
        pass

    @send_key
    def test_0220_KEY_ZOOM2(self):
        """Zoom 2 key test"""
        pass


    def test_999_DISCONNECT(self):
        if self.remote is None:
            self.skipTest('no connection')
        else:
            self.remote.close()

    def on_disconnect(self):
        pass

    def on_connect(self, message):

        payload = (
            b"\x64\x00" +
            self._serialize_string(self.config["description"]) +
            self._serialize_string(self.config["id"]) +
            self._serialize_string(self.config["name"])
        )
        packet = b"\x00\x00\x00" + self._serialize_string(payload, True)

        self.assertEquals(packet, message)

        tv_name = self.config["name"]
        tv_name_len = bytearray.fromhex(hex(len(tv_name))[2:].zfill(2))

        while len(tv_name_len) < 3:
            tv_name_len = '\x00' + tv_name_len

        packet1 = tv_name_len + tv_name + b"\x00\x01\x0a"
        packet2 = tv_name_len + tv_name + b"\x00\x04\x64\x00\x01\x00"

        self.client.send(packet1)
        self.client.send(packet2)
        self.connection_event.set()

if __name__ == '__main__':

    base_path = os.path.dirname(__file__)

    if not base_path:
        base_path = os.path.dirname(sys.argv[0])

    if not base_path:
        base_path = os.getcwd()

    sys.path.insert(0, os.path.join(base_path, '..'))

    import samsungctl

    sys.argv.append()
    unittest.main()

else:
    import samsungctl
