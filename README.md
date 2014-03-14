samsungctl
==========
samsungctl is a library and a command line tool for remote controlling Samsung
televisions via TCP/IP connection.

Dependencies
------------
samsungctl requires Python 3, but currently no additional libraries.

Command line tool quick help
----------------------------
The command line tool can be installed with

	python setup.py install

or run without installation with

	python -m samsungctl

Use ```--help``` for more information about the command line arguments.

The settings can be loaded from a configuration file, which is searched from
```$XDG_CONFIG_HOME/samsungctl.conf``` and ```~/.config/samsungctl.conf```. A
simple default configuration is bundled with the source as
[samsungctl.conf](samsungctl.conf).

Supported models
----------------
- UE40EH6030
- probably almost all modern Samsung TVs with ethernet or Wi-Fi connection

Roadmap
-------
- Read the response from TV
	- Show error messages
	- Wait for user authorization

References
----------
I did not reverse engineer the control protocol myself and samsungctl is not
the only implementation. Here is the list of things that inspired samsungctl.

- http://sc0ty.pl/2012/02/samsung-tv-network-remote-control-protocol/
- https://gist.github.com/danielfaust/998441
- https://github.com/Bntdumas/SamsungIPRemote
