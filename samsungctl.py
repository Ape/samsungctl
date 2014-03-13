#!/usr/bin/env python

import argparse
import base64
import socket
import sys
import time

class Remote():
	def __init__(self, addr, port, name, description, id):
		self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connection.connect((addr, port))

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

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Remote control Samsung televisions via TCP/IP connection.",
	                                 epilog="E.g. {0} --name myremote 192.168.0.10 KEY_VOLDOWN".format(sys.argv[0]))
	parser.add_argument("ip", help="TV IP address")
	parser.add_argument("key", help="key to be sent (e.g. KEY_VOLDOWN)")
	parser.add_argument("--name", default="samsungctl", help="remote control name")
	parser.add_argument("--description", default="PC", help="remote control description")
	parser.add_argument("--id", default="", help="remote control id")
	parser.add_argument("--port", type=int, default=55000, help="TV port number (TCP)")

	args = parser.parse_args()

	with Remote(args.ip, args.port, args.name, args.description, args.id) as remote:
		remote.control(args.key)
