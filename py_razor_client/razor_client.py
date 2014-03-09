# -*- coding: utf-8 -*-
"""Contains a quick-and-dirty client for talking to a Razor server.

Rather than enumerating an API that has lots of warning labels and stickers
cautioning that the API might change frequently, I'm letting the razor server
drive. This class will, when given a host and port, ask razor for its API
capabilities. For each collection it finds (things like nodes, repos, etc), two
methods will be bound to this class: a lister (the plural noun) and a getter
(the singular noun). For each command it finds, a method with the same name
is bound to the class after a bit of sanitization (at this time, just changing
hyphens to underscores to make Python happy). Similar sanitization happens to
any conflicting argument names for commands.

Example usage:
    client = RazorClient("example.com", 8080)
    client.repos()
    client.nodes()
    client.nodes("node1")
    client.create_repo(name="test_repo", iso_url="http://example.com/img.iso")
"""
from functools import partial
import json
import urlparse

import requests


class RazorClient(object):

    # The below tranformation mapping is somewhat unfortunate, but ultimately
    # necessary to fit in here, since arguments like iso-url can't be specified
    # as python keywords.
    ARG_TRANSFORMS = {
        "broker_type": "broker-type",
        "iso_url": "iso-url",
    }
    API_PATH = "/api"  # It's less likely that this will change

    def __init__(self, hostname, port, lazy_discovery=False):
        self.hostname = hostname
        self.port = str(port)
        self._collection_urls = {}
        self.collections = set()
        self.commands = set()

        if not lazy_discovery:
            self.discover_methods()

    def get_path(self, path, response_as_json=True):
        url = self._coerce_to_full_url(path)
        response = requests.get(url)
        response.raise_for_status()  # makes sure errors get propagated as exceptions
        if response_as_json:
            return response.json()
        else:
            return response.text

    def post_data(self, path, **data):
        url = self._coerce_to_full_url(path)
        headers = {
            "Content-Type": "application/json",
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        return response.json()

    def discover_methods(self):
        methods_data = self.get_path("/api")
        for collection in methods_data['collections']:
            self._bind_collection(collection)
        for command in methods_data['commands']:
            self._bind_command(command)

    def sanitize_command_name(self, name):
        return name.replace("-", "_")

    def _coerce_to_full_url(self, maybe_path):
        """Turns what might be a relative path into an asbolute URL."""
        if not maybe_path.startswith("http"):
            url = self._make_razor_url(maybe_path)
        else:
            url = maybe_path

        return url

    def _make_netloc(self):
        return ":".join((self.hostname, self.port))

    def _make_razor_url(self, path):
        netloc = self._make_netloc()
        return urlparse.urlunsplit(("http", netloc, path, "", ""))

    def _bind_collection(self, collection):
        collection_name = collection['name']
        collection_url = collection['id']

        self._bind_method(collection_name, lambda *args, **kwargs: self._get_collection(collection_url, *args, **kwargs))
        self.collections.add(collection_name)

    def _bind_command(self, command):
        command_name = command['name']
        command_url = command['id']

        # Sanitize the command name so that it maps to something we can call
        # as a python identifier
        command_name = self.sanitize_command_name(command_name)

        self._bind_method(command_name, partial(self._execute_command, command_url))
        self.commands.add(command_name)

    def _bind_method(self, method_name, method):
        setattr(self, method_name, method)

    def _get_collection(self, url, *item):
        if item:
            item_path = '/'.join(item)
            total_item_path = '/'.join((url, item_path))
        else:
            total_item_path = url
        return self.get_path(total_item_path)

    def _execute_command(self, url, **kwargs):
        for key in kwargs.keys():
            if key in self.ARG_TRANSFORMS:
                kwargs[self.ARG_TRANSFORMS[key]] = kwargs[key]
                del kwargs[key]
        return self.post_data(url, **kwargs)
