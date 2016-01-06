import base64
import logging
import socket
import time

class Remote():
    class AccessDenied(Exception):
        pass

    class UnhandledResponse(Exception):
        pass

    def __init__(self, host, port, name, description, id):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((host, port))

        payload = b"\x64\x00" +\
                  self._serialize_string(str.encode(description)) +\
                  self._serialize_string(str.encode(id)) +\
                  self._serialize_string(str.encode(name))
        packet = b"\x00\x00\x00" + self._serialize_string(payload, True)

        logging.info("Sending handshake.")
        self.connection.send(packet)
        self._read_response(True)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self.connection.close()

    def control(self, key):
        payload = b"\x00\x00\x00" + self._serialize_string(str.encode(key))
        packet = b"\x00\x00\x00" + self._serialize_string(payload, True)

        logging.info("Sending control command.")
        self.connection.send(packet)
        self._read_response()
        time.sleep(self._key_interval)

    _key_interval = 0.2

    def _read_response(self, first_time=False):
        header = self.connection.recv(3)
        tv_name_len = int.from_bytes(header[1:3],
                                     byteorder="little")
        tv_name = self.connection.recv(tv_name_len)

        response_len = int.from_bytes(self.connection.recv(2),
                                      byteorder="little")
        response = self.connection.recv(response_len)

        if response == b"\x64\x00\x01\x00":
            logging.debug("Access granted.")
            return
        elif response == b"\x64\x00\x00\x00":
            raise self.AccessDenied()
        elif response[0:1] == b"\x0a":
            if first_time:
                logging.warning("Waiting for authorization...")
            return self._read_response()
        elif response[0:1] == b"\x65":
            logging.warning("Authorization cancelled.")
            raise self.AccessDenied()
        elif response == b"\x00\x00\x00\x00":
            logging.debug("Control accepted.")
            return

        raise self.UnhandledResponse(response)

    @staticmethod
    def _serialize_string(string, raw = False):
        if not raw:
            string = base64.b64encode(string)

        return bytes([len(string)]) + b"\x00" + string
