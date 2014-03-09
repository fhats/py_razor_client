# -*- coding: utf-8 -*-
import os
from setuptools import setup

from py_razor_client.version import VERSION


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="py_razor_client",
    version=VERSION,
    author="Fred Hatfull",
    author_email="fred.hatfull@gmail.com",
    description=("A simple Python library for interacting with Razor"),
    license="MIT",
    keywords="razor razor-server imaging library",
    url="http://packages.python.org/py_razor_client",
    packages=['py_razor_client', 'tests'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: System :: Installation/Setup",
    ],
    install_requires=[
        "argparse == 1.2.1",
        "requests == 2.2.0",
    ],
    tests_require=[
        "coverage == 3.7.1",
        "mock == 1.0.1",
        "testify == 0.5.2"
    ]
)
