# -*- coding: utf-8 -*-

from . import exceptions
from .remote_legacy import RemoteLegacy
from .remote_websocket import RemoteWebsocket

try:
    from .remote_encrypted import RemoteEncrypted
except ImportError:
    RemoteEncrypted = None

import logging

logger = logging.getLogger('samsungctl')


class Remote:
    def __init__(self, config, log_level=None):
        logging.basicConfig(format="%(message)s", level=log_level)
        if log_level is not None:
            logger.setLevel(log_level)

        if config["method"] == "legacy":
            self.remote = RemoteLegacy(config)
        elif config["method"] == "websocket":
            self.remote = RemoteWebsocket(config)
        elif config["method"] == "encrypted":
            if RemoteEncrypted is None:
                raise RuntimeError(
                    'Python 2 is not currently supported '
                    'for H and J model year TV\'s'
                )
            
            self.remote = RemoteEncrypted(config)
        else:
            raise exceptions.UnknownMethod()

    def __enter__(self):
        return self.remote.__enter__()

    def __exit__(self, type, value, traceback):
        self.remote.__exit__(type, value, traceback)

    def close(self):
        return self.remote.close()

    def control(self, key):
        return self.remote.control(key)
