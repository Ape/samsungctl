samsungctl
==========
samsungctl is a library and a command line tool for remote controlling Samsung
televisions via TCP/IP connection. It should work with any modern Samsung TV
with Ethernet or Wi-Fi connection.

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

References
----------
I did not reverse engineer the control protocol myself and samsungctl is not
the only implementation. Here is the list of things that inspired samsungctl.

- http://sc0ty.pl/2012/02/samsung-tv-network-remote-control-protocol/
- https://gist.github.com/danielfaust/998441
- https://github.com/Bntdumas/SamsungIPRemote
