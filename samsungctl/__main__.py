import argparse
import collections
import json
import logging
import os
import socket

from . import __doc__
from . import __title__
from . import __version__
from . import interactive
from .remote import Remote

def _read_config():
    config = collections.defaultdict(lambda: None, {
        "name": "samsungctl",
        "description": "PC",
        "id": "",
        "port": 55000,
        "timeout": 0,
    })

    file_loaded = False
    directories = []

    xdg_config = os.getenv("XDG_CONFIG_HOME")
    if xdg_config:
        directories.append(xdg_config)

    directories.append(os.path.join(os.getenv("HOME"), ".config"))
    directories.append("/etc")

    for directory in directories:
        try:
            config_file = open(os.path.join(directory, "samsungctl.conf"))
        except FileNotFoundError:
            continue
        else:
            file_loaded = True
            break

    if not file_loaded:
        return config

    with config_file:
        try:
            config_json = json.load(config_file)
        except ValueError as e:
            logging.warning("Warning: Could not parse the configuration file.\n  %s", e)
            return config

        config.update(config_json)

    return config

def main():
    parser = argparse.ArgumentParser(prog=__title__, description=__doc__,
                                     epilog="E.g. %(prog)s --host 192.168.0.10 --name myremote KEY_VOLDOWN")
    parser.add_argument("--version", action="version", version="%(prog)s {0}".format(__version__))
    parser.add_argument("-v", "--verbose", action="count", help="increase output verbosity")
    parser.add_argument("-q", "--quiet", action="store_true", help="suppress non-fatal output")
    parser.add_argument("key", nargs="*", help="keys to be sent (e.g. KEY_VOLDOWN)")
    parser.add_argument("--host", help="TV hostname or IP address")
    parser.add_argument("--name", help="remote control name")
    parser.add_argument("--description", help="remote control description")
    parser.add_argument("--id", help="remote control id")
    parser.add_argument("--port", type=int, help="TV port number (TCP)")
    parser.add_argument("-i", "--interactive", action="store_true", help="interactive control")
    parser.add_argument("--timeout", type=float, help="socket timeout in seconds (0 = no timeout)")

    args = parser.parse_args()

    if args.quiet:
        log_level = logging.ERROR
    elif not args.verbose:
        log_level = logging.WARNING
    elif args.verbose == 1:
        log_level = logging.INFO
    else:
        log_level = logging.DEBUG

    logging.basicConfig(format="%(message)s", level=log_level)

    if not args.key and not args.interactive:
        logging.error("Error: At least one key or --interactive must be set.")
        return

    config = _read_config()

    host = args.host or config["host"]
    name = args.name or config["name"]
    description = args.description or config["description"]
    id = args.id or config["id"]
    port = args.port or config["port"]
    timeout = args.timeout or config["timeout"]

    if not host:
        logging.error("Error: --host must be set")
        return

    try:
        remote = Remote(host, port, name, description, id, timeout)
    except Remote.AccessDenied:
        logging.error("Error: Access denied!")
    except socket.timeout:
        logging.error("Error: Timed out!")
    except OSError as e:
        logging.error("Error: {}".format(e.strerror))
    else:
        with remote:
            if args.interactive:
                interactive.run(remote)
            else:
                for key in args.key:
                    remote.control(key)

if __name__ == "__main__":
    main()
