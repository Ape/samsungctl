#!/usr/bin/env python

import setuptools

setuptools.setup(name="samsungctl",
      version="0.1.0",
      description="Remote control Samsung televisions via TCP/IP connection",
      url="https://github.com/Ape/samsungctl",
      author="Lauri Niskanen",
      author_email="ape@ape3000.com",
      license="MIT",
      long_description=open("README.md").read(),
      entry_points={
        "console_scripts": ["samsungctl=samsungctl.__main__"]
      },
      packages=["samsungctl"],
      install_requires=[],
      classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Home Automation"
      ]
)
