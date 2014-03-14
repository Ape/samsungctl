#!/usr/bin/env python

import base64
import socket
import time

class Remote():
	def __init__(self, host, port, name, description, id):
		self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connection.connect((host, port))

		payload = b"\x64\x00" +\
		          self._serialize_string(str.encode(description)) +\
		          self._serialize_string(str.encode(id)) +\
		          self._serialize_string(str.encode(name))
		packet = b"\x00\x00\x00" + self._serialize_string(payload, True)

		self.connection.send(packet)

	def __enter__(self):
		return self

	def __exit__(self, type, value, traceback):
		self.close()

	def close(self):
		self.connection.close()

	def control(self, key):
		payload = b"\x00\x00\x00" + self._serialize_string(str.encode(key))
		packet = b"\x00\x00\x00" + self._serialize_string(payload, True)

		self.connection.send(packet)
		time.sleep(self._key_interval)

	_key_interval = 0.25

	@staticmethod
	def _serialize_string(string, raw = False):
		if not raw:
			string = base64.b64encode(string)

		return bytes([len(string)]) + b"\x00" + string
