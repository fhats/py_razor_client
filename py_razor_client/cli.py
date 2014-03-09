# -*- coding: utf-8 -*-
import os.path
from urlparse import urlparse
import yaml


RC_LOCATIONS = (os.path.expanduser("~/.py_razor_clientrc"),
                os.path.join("/", "etc", "py_razor_client"))


class NoSuchConfigFileException(Exception):
    pass


class InsufficientHostException(Exception):
    pass


def dynamicize_argparser(parser, args):
    """Given an ArgumentParser, tries to coerce the ArgumentParser to have
    options for each unknown --longopt it encounters.

    This exists to provide a compatibility shim to allow this tool to be used
    in the same manner as the pure-ruby optparse that powers razor-client.
    """
    _, unknown_args = parser.parse_known_args(args)
    unknown_longopts = filter_for_longopts(unknown_args)

    added_args = []

    for opt in unknown_longopts:
        add_result = parser.add_argument(opt)
        dest = add_result.dest
        added_args.append(dest)

    return (parser, added_args)


def filter_for_longopts(arglist):
    """Given a list of arguments, filter out any that aren't --longopts."""
    return filter(lambda x: x.startswith("--"), arglist)


def load_config(config_file=None):
    """Loads a configuration from a given file, from ~/.py_razor_clientrc, or
    /etc/py_razor_client if it exists.

    Precedence is always given to a config file specified on the command line.
    """
    if config_file:
        if not os.path.exists(config_file):
            raise NoSuchConfigFileException()
    else:
        rc_files = filter(os.path.exists, RC_LOCATIONS)
        if rc_files:
            config_file = rc_files[0]
        else:
            config_file = None

    if config_file:
        with open(config_file) as f:
            return yaml.load(f.read())
    else:
        return {}


def make_config(args):
    config = vars(args)
    config.update(load_config(args.config))

    if config['url']:
        bits = urlparse(config['url'])
        host = bits[1]
        hostname, port = host.split(":")
        config.update(hostname=hostname, port=port)
        del config['url']

    if not (config['hostname'] and config['port']):
        raise InsufficientHostException()

    return config
