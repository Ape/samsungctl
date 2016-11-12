from . import exceptions
from .remote_legacy import RemoteLegacy
from .remote_websocket import RemoteWebsocket

class Remote:
    def __init__(self, config):
        if config["method"] == "legacy":
            self.remote = RemoteLegacy(config)
        elif config["method"] == "websocket":
            self.remote = RemoteWebsocket(config)
        else:
            raise exceptions.UnknownMethod()

    def close(self):
        return self.remote.close()

    def control(self, key):
        return self.remote.control(key)
