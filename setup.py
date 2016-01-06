#!/usr/bin/env python

import setuptools

import samsungctl

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
    install_requires=[],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Home Automation",
    ],
)
