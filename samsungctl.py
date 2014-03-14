#!/usr/bin/env python

import argparse
import base64
import collections
import json
import os
import socket
import sys
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

def read_config():
	config = collections.defaultdict(lambda: None, {
		"name": "samsungctl",
		"description": "PC",
		"id": "",
		"port": 55000,
	})

	config_directory = os.getenv("XDG_CONFIG_HOME") or os.path.join(os.getenv("HOME"), ".config")

	try:
		config_file = open(os.path.join(config_directory, "samsungctl.conf"))
	except FileNotFoundError:
		return config

	with config_file:
		try:
			config_json = json.load(config_file)
		except ValueError as e:
			print("Warning: Could not parse the configuration file.")
			print(e)
			print()
			return config

		config.update(config_json)

	return config

if __name__ == "__main__":
	config = read_config()

	parser = argparse.ArgumentParser(description="Remote control Samsung televisions via TCP/IP connection.",
	                                 epilog="E.g. {0} --host 192.168.0.10 --name myremote KEY_VOLDOWN".format(sys.argv[0]))
	parser.add_argument("key", help="key to be sent (e.g. KEY_VOLDOWN)")
	parser.add_argument("--host", default=config["host"], help="TV hostname or IP address")
	parser.add_argument("--name", default=config["name"], help="remote control name")
	parser.add_argument("--description", default=config["description"], help="remote control description")
	parser.add_argument("--id", default=config["id"], help="remote control id")
	parser.add_argument("--port", type=int, default=config["port"], help="TV port number (TCP)")

	args = parser.parse_args()

	if not args.host:
		print("Error: --host must be set")
		parser.print_help()
		sys.exit()

	with Remote(args.host, args.port, args.name, args.description, args.id) as remote:
		remote.control(args.key)
