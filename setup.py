# -*- coding: utf-8 -*-
import os
from setuptools import setup

from py_razor_client.version import VERSION

setup(
    name="py_razor_client",
    version=VERSION,
    author="Fred Hatfull",
    author_email="fred.hatfull@gmail.com",
    description=("A simple Python library for interacting with Razor"),
    license="MIT",
    keywords="razor razor-server imaging library",
    url="https://github.com/fhats/py_razor_client",
    packages=['py_razor_client', 'tests'],
    long_description="A pure-python Razor client. See https://github.com/fhats/py_razor_client for more information.",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: System :: Installation/Setup",
    ],
    scripts=['bin/py-razor-client'],
    install_requires=[
        "argparse >= 1.0.0",
        "requests == 2.2.0",
        "pyyaml >= 3.0.0",
    ],
    tests_require=[
        "coverage == 3.7.1",
        "mock == 1.0.1",
        "testify == 0.5.2"
    ]
)
