#!/usr/bin/env python
import sys

try:
    import websocket

    websocket_version = tuple(websocket.__version__.split('.'))
    if websocket_version > (0, 48, 0):
        answer = input(
            'The version of the websocket-client library that is currently\n'
            'installed is newer then the one that is needed by samsungctl.\n'
            'There are bugs in the version that is installed that will \n'
            'cause problems with samsungctl.\n\n'
            'Would you like to downgrade the websocket-client library? (Y/N)'
        )

        answer = answer.lower()
        if not answer.strip() or answer.strip()[0] != 'y':
            sys.exit(1)

        try:
            from pip import main
        except ImportError:
            from pip._internal import main

        main(['install', '--uninstall', 'websocket-client'])

        for mod_name in list(sys.modules.keys())[:]:
            if mod_name.startswith('websocket.') or mod_name == 'websocket':
                try:
                    del sys.modules[mod_name]
                except KeyError:
                    pass

except ImportError:
    websocket = None

import setuptools
import samsungctl

del websocket

setuptools.setup(
    name=samsungctl.__title__,
    version=samsungctl.__version__,
    description=samsungctl.__doc__,
    url=samsungctl.__url__,
    author=samsungctl.__author__,
    author_email=samsungctl.__author_email__,
    license=samsungctl.__license__,
    long_description=open("README.md").read(),
    entry_points={
        "console_scripts": ["samsungctl=samsungctl.__main__:main"]
    },
    packages=["samsungctl"],
    install_requires=["websocket-client==0.48.0"],
    extras_require={
        "interactive_ui": ["curses"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Home Automation",
    ],
)
