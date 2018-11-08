from __future__ import print_function
import argparse
import collections
import json
import logging
import os
import socket
import errno

from . import __doc__ as doc
from . import __title__ as title
from . import __version__ as version
from . import exceptions
from . import Remote
from . import key_mappings


def _read_config():
    config = collections.defaultdict(lambda: None, {
        "name": "samsungctl",
        "description": "PC",
        "id": "",
        "method": "legacy",
        "timeout": 0,
    })

    directories = []

    app_data = os.getenv('APPDATA')

    if app_data:
        app_data = os.path.join(app_data, "samsungctl")
        if not os.path.exists(app_data):
            os.mkdir(app_data)

        directories.append(app_data)
    else:
        xdg_config = os.getenv("XDG_CONFIG_HOME")
        if xdg_config:
            directories.append(xdg_config)

        directories.append(os.path.join(os.getenv("HOME"), ".config"))
        directories.append("/etc")

    for directory in directories:
        try:
            with open(os.path.join(directory, "samsungctl.conf"), 'r') as f:
                config_json = json.load(f)
            config.update(config_json)

        except ValueError as e:
            message = "Warning: Could not parse the configuration file.\n  %s"
            logging.warning(message, e)
            break

        except IOError as e:
            if e.errno != errno.ENOENT:
                raise e

    return config


def keys_help(keys):
    import sys

    key_groups = {}
    max_len = 0

    if not keys or keys == [None]:
        keys = key_mappings.KEYS.values()

    for key in keys:
        if key is None:
            continue

        group = key.group
        key = str(key)
        if group not in key_groups:
            key_groups[group] = []

        if key not in key_groups[group]:
            key_groups[group] += [key]
            max_len = max(max_len, len(key) - 4)

    print('Available keys')
    print('=' * (max_len + 4))
    print()
    print('Note: Key support depends on TV model.')
    print()

    for group in sorted(list(key_groups.keys())):
        print('    ' + group)
        print('    ' + ('-' * max_len))
        print('\n'.join(key_groups[group]))
        print()
    sys.exit(0)


def get_key(key):
    if key in key_mappings.KEYS:
        return key_mappings.KEYS[key]
    else:
        logging.warning("Warning: Key {0} not found.".format(key))


def main():
    epilog = "E.g. %(prog)s --host 192.168.0.10 --name myremote KEY_VOLDOWN"
    parser = argparse.ArgumentParser(prog=title, description=doc,
                                     epilog=epilog)
    parser.add_argument("--version", action="version",
                        version="%(prog)s {0}".format(version))
    parser.add_argument("-v", "--verbose", action="count",
                        help="increase output verbosity")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="suppress non-fatal output")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="interactive control")
    parser.add_argument("--host", help="TV hostname or IP address")
    parser.add_argument("--port", type=int, help="TV port number (TCP)")
    parser.add_argument("--method",
                        help="Connection method (legacy or websocket)")
    parser.add_argument("--name", help="remote control name")
    parser.add_argument("--description", metavar="DESC",
                        help="remote control description")
    parser.add_argument("--id", help="remote control id")
    parser.add_argument("--timeout", type=float,
                        help="socket timeout in seconds (0 = no timeout)")
    parser.add_argument("--key-help", action="store_true",
                        help="print available keys. (key support depends on tv model)")
    parser.add_argument("key", nargs="*", default=[], type=get_key,
                        help="keys to be sent (e.g. KEY_VOLDOWN)")

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

    if args.key_help:
        keys_help(args.key)

    config = _read_config()
    config.update({k: v for k, v in vars(args).items() if v is not None})

    if not config["host"]:
        logging.error("Error: --host must be set")
        return

    try:
        with Remote(config) as remote:
            for key in args.key:
                if key is None:
                    continue
                key(remote)

            if args.interactive:
                logging.getLogger().setLevel(logging.ERROR)
                from . import interactive
                interactive.run(remote)
            elif len(args.key) == 0:
                logging.warning("Warning: No keys specified.")
    except exceptions.ConnectionClosed:
        logging.error("Error: Connection closed!")
    except exceptions.AccessDenied:
        logging.error("Error: Access denied!")
    except exceptions.UnknownMethod:
        logging.error("Error: Unknown method '{}'".format(config["method"]))
    except socket.timeout:
        logging.error("Error: Timed out!")
    except OSError as e:
        logging.error("Error: %s", e.strerror)


if __name__ == "__main__":
    main()
