samsungctl
==========
samsungctl is a library and a command line tool for remote controlling Samsung
televisions via a TCP/IP connection. It should work with any modern Samsung TV
with Ethernet or Wi-Fi connectivity.

Dependencies
------------
samsungctl requires Python 3, but no additional libraries.

Installation
------------
samsungctl can be installed using [pip](https://pip.pypa.io/):

	# pip install samsungctl

Alternatively you can clone the Git repository and run:

	# python setup.py install

It's possible to use the command line tool without installation:

	$ python -m samsungctl

Command line usage
------------------

Use `samsungctl --help` for information about the command line arguments:

```
usage: samsungctl [-h] [--version] [-v] [-q] [-i] [--host HOST] [--port PORT]
                  [--name NAME] [--description DESC] [--id ID]
                  [--timeout TIMEOUT]
                  [key [key ...]]

Remote control Samsung televisions via TCP/IP connection

positional arguments:
  key                 keys to be sent (e.g. KEY_VOLDOWN)

optional arguments:
  -h, --help          show this help message and exit
  --version           show program's version number and exit
  -v, --verbose       increase output verbosity
  -q, --quiet         suppress non-fatal output
  -i, --interactive   interactive control
  --host HOST         TV hostname or IP address
  --port PORT         TV port number (TCP)
  --name NAME         remote control name
  --description DESC  remote control description
  --id ID             remote control id
  --timeout TIMEOUT   socket timeout in seconds (0 = no timeout)

E.g. samsungctl --host 192.168.0.10 --name myremote KEY_VOLDOWN
```

The settings can be loaded from a configuration file. The file is searched from
`$XDG_CONFIG_HOME/samsungctl.conf`, `~/.config/samsungctl.conf`, and
`/etc/samsungctl.conf` in this order. A simple default configuration is bundled
with the source as [samsungctl.conf](samsungctl.conf).

Library usage
-------------

samsungctl can be imported as a Python 3 library:

```python
import samsungctl
```

A context managed remote controller object of class `Remote` can be constructed
using the `with` statement:

```python
with samsungctl.Remote(config) as remote:
    # Use the remote object
```

The constructor takes a configuration dictionary as a parameter. All
configuration items must be specified.

| Key         | Type   | Description                               |
| ----------- | ------ | ----------------------------------------- |
| host        | string | Hostname or IP address of the TV.         |
| port        | int    | TCP port number. (Default: `55000`)       |
| name        | string | Name of the remote controller.            |
| description | string | Remote controller description.            |
| id          | string | Additional remote controller ID.          |
| timeout     | int    | Timeout in seconds. `0` means no timeout. |

The `Remote` object is very simple and you only need the `control(key)` method.
The only parameter is a string naming the key to be sent (e.g.
`"KEY_VOLDOWN"`). The list of accepted keys may vary depending on the TV model,
but [interactive.py#L3](samsungctl/interactive.py#L3) (the second column) can
be used as reference. You can call `control` multiple times using the same
`Remote` object. The connection is automatically closed when exiting the `with`
statement.

When something goes wrong you will receive an exception:

| Exception                | Description                             |
| ------------------------ | --------------------------------------- |
| Remote.AccessDenied      | The TV does not allow you to send keys. |
| Remote.ConnectionClosed  | The connection was closed.              |
| Remote.UnhandledResponse | An unexpected response was received.    |
| socket.timeout           | The connection timed out.               |

### Example program

This simple program opens and closes the menu a few times.

```python
#!/usr/bin/env python3

import samsungctl
import time

config = {
    "name": "samsungctl",
    "description": "PC",
    "id": "",
    "host": "192.168.0.10",
    "port": 55000,
    "timeout": 0,
}

with samsungctl.Remote(config) as remote:
    for i in range(10):
        remote.control("KEY_MENU")
        time.sleep(0.5)
```

References
----------
I did not reverse engineer the control protocol myself and samsungctl is not
the only implementation. Here is the list of things that inspired samsungctl.

- http://sc0ty.pl/2012/02/samsung-tv-network-remote-control-protocol/
- https://gist.github.com/danielfaust/998441
- https://github.com/Bntdumas/SamsungIPRemote
