# A Python client for the Razor API

[![Build Status](https://travis-ci.org/fhats/py_razor_client.png?branch=master)](https://travis-ci.org/fhats/py_razor_client)

[py_razor_client](https://github.com/fhats/py_razor_client) is a Python client for Puppetlab's excellent [Razor](https://github.com/puppetlabs/puppetlabs-razor) imaging project. 

## In Your Code

```
>>> from py_razor_client.razor_client import RazorClient
>>> client = RazorClient("localhost", 8080)
>>> client.collections
set([u'node', u'tags', u'policie', u'repos', u'broker', u'repo', u'tag', u'brokers', u'policies', u'nodes'])
>>> client.commands
set([u'unbind_node', u'create_installer', u'delete_node', u'create_policy', u'delete_tag', u'create_tag', u'create_broker', u'delete_repo', u'enable_policy', u'create_repo', u'update_tag_rule', u'disable_policy'])
>>> client.nodes()
[{u'spec': u'http://api.puppetlabs.com/razor/v1/collections/nodes/member', u'name': u'node1', u'id': u'http://localhost:8080/api/collections/nodes/node1'}]
```