#!/usr/bin/env python

import argparse
import collections
import json
import os
import sys

from . import __title__
from . import __version__
from .remote import Remote

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

def main():
	config = read_config()

	parser = argparse.ArgumentParser(prog=__title__,
									 description="Remote control Samsung televisions via TCP/IP connection.",
									 epilog="E.g. %(prog)s --host 192.168.0.10 --name myremote KEY_VOLDOWN")
	parser.add_argument("--version", action="version", version="%(prog)s {0}".format(__version__))
	parser.add_argument("key", nargs="+", help="keys to be sent (e.g. KEY_VOLDOWN)")
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
		for key in args.key:
			remote.control(key)

main()
