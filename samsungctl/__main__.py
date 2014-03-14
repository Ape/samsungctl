#!/usr/bin/env python

import argparse
import collections
import json
import os
import sys

from . import remote

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

with remote.Remote(args.host, args.port, args.name, args.description, args.id) as remote:
	remote.control(args.key)
