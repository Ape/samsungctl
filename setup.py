#!/usr/bin/env python
import setuptools # NOQA

__title__ = "samsungctl"
__version__ = "0.8.0b"
__url__ = "https://github.com/kdschlosser/samsungctl"
__author__ = "Lauri Niskanen, Kevin Schlosser"
__author_email__ = "kevin.g.schlosser@gmail.com"
__license__ = "MIT"

setuptools.setup(
    name=__title__,
    version=__version__,
    description=__doc__,
    url=__url__,
    author=__author__,
    author_email=__author_email__,
    license=__license__,
    long_description=open("README.md").read(),
    entry_points={
        "console_scripts": ["samsungctl=samsungctl.__main__:main"]
    },
    packages=["samsungctl"],
    install_requires=["websocket-client", "requests"],
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
    zip_safe=False
)
