# -*- coding: utf-8 -*-
from contextlib import nested
import json
import mock
import testify as T
from urlparse import urlunsplit

from py_razor_client.razor_client import RazorClient


class RazorClientTestCase(T.TestCase):

    @T.setup_teardown
    def create_razor_client(self):
        self.hostname = "some_host"
        self.port = "some_port"
        requests_tgt = "py_razor_client.razor_client.requests"
        requests_mock = mock.patch(requests_tgt)

        with requests_mock as self.mock_requests:
            self.razor_client = RazorClient(self.hostname, self.port, True)
            self.mock_requests.reset_mock()
            yield

    def make_json_response(self, expected_response):
        mock_response = mock.Mock()
        mock_response.json.return_value = expected_response
        return mock_response

    def make_text_response(self, expected_response):
        mock_response = mock.Mock()
        mock_response.text = expected_response
        return mock_response


class ConstructorTest(RazorClientTestCase):

    @T.setup_teardown
    def mock_discover_methods(self):
        disc_tgt = "py_razor_client.razor_client.RazorClient.discover_methods"
        with mock.patch(disc_tgt) as self.mock_discover_methods:
            yield

    def test_constructor_attributes(self):
        razor_client = RazorClient(self.hostname, self.port)

        T.assert_equal(razor_client.hostname, self.hostname)
        T.assert_equal(razor_client.port, str(self.port))

    def test_lazy_discovery_on(self):
        RazorClient(self.hostname, self.port, lazy_discovery=True)
        T.assert_equal(self.mock_discover_methods.call_count, 0)

    def test_lazy_discovery_off(self):
        RazorClient(self.hostname, self.port, lazy_discovery=False)
        self.mock_discover_methods.assert_called_once_with()


class DiscoverMethodsTest(RazorClientTestCase):

    def test_discover_methods(self):
        collections = ('one', 'two')
        commands = ('red', 'blue')
        mock_response = self.make_json_response({
            "collections": collections,
            "commands": commands
        })
        self.mock_requests.get.return_value = mock_response

        bind_mocks = (mock.patch.object(self.razor_client, "_bind_collection"),
                      mock.patch.object(self.razor_client, "_bind_command"))
        ctxt = nested(*bind_mocks)

        with ctxt as (mock_bind_collection, mock_bind_command):
            self.razor_client.discover_methods()

            T.assert_equal(mock_bind_collection.call_count, 2)
            for collection in collections:
                mock_bind_collection.assert_any_call(collection)

            T.assert_equal(mock_bind_command.call_count, 2)
            for command in commands:
                mock_bind_command.assert_any_call(command)


class GetPathTest(RazorClientTestCase):

    def test_get_path_relative_url_with_json(self):
        expected_response = mock.sentinel.response
        mock_response = self.make_json_response(expected_response)
        self.mock_requests.get.return_value = mock_response

        test_path = "/api/collections/nodes"
        expected_host = ":".join((self.hostname, self.port))
        expected_path = urlunsplit(("http", expected_host, test_path, "", ""))

        actual_response = self.razor_client.get_path(test_path, True)

        T.assert_equal(expected_response, actual_response)
        self.mock_requests.get.assert_called_once_with(expected_path)

    def test_get_path_relative_url_with_text(self):
        expected_response = mock.sentinel.response
        mock_response = self.make_text_response(expected_response)
        self.mock_requests.get.return_value = mock_response

        test_path = "/api/collections/nodes"
        expected_host = ":".join((self.hostname, self.port))
        expected_path = urlunsplit(("http", expected_host, test_path, "", ""))

        actual_response = self.razor_client.get_path(test_path, False)

        T.assert_equal(expected_response, actual_response)
        self.mock_requests.get.assert_called_once_with(expected_path)

    def test_get_path_absolute_url_with_json(self):
        expected_response = mock.sentinel.response
        mock_response = self.make_json_response(expected_response)
        self.mock_requests.get.return_value = mock_response

        test_path = "http://%s:%s/api/collections/nodes" % (self.hostname,
                                                            self.port)
        expected_path = test_path

        actual_response = self.razor_client.get_path(test_path, True)

        T.assert_equal(expected_response, actual_response)
        self.mock_requests.get.assert_called_once_with(expected_path)

    def test_get_path_absolute_url_with_text(self):
        expected_response = mock.sentinel.response
        mock_response = self.make_text_response(expected_response)
        self.mock_requests.get.return_value = mock_response

        test_path = "http://%s:%s/api/collections/nodes" % (self.hostname,
                                                            self.port)
        expected_path = test_path

        actual_response = self.razor_client.get_path(test_path, False)

        T.assert_equal(expected_response, actual_response)
        self.mock_requests.get.assert_called_once_with(expected_path)


class PostDataTest(RazorClientTestCase):

    def test_relative_path(self):
        expected_response = mock.sentinel.response
        mock_response = self.make_json_response(expected_response)
        self.mock_requests.post.return_value = mock_response

        test_path = "/api/commands/delete_node"
        expected_host = ":".join((self.hostname, self.port))
        expected_path = urlunsplit(("http", expected_host, test_path, "", ""))
        expected_headers = {
            "Content-Type": "application/json"
        }
        expected_data = "{}"

        actual_response = self.razor_client.post_data(test_path)

        T.assert_equal(expected_response, actual_response)
        self.mock_requests.post.assert_called_once_with(
            expected_path,
            headers=expected_headers,
            data=expected_data)

    def test_absolute_path(self):
        expected_response = mock.sentinel.response
        mock_response = self.make_json_response(expected_response)
        self.mock_requests.post.return_value = mock_response

        test_path = "http://%s:%s/api/commands/delete_node" % (self.hostname,
                                                               self.port)
        expected_path = test_path
        expected_headers = {
            "Content-Type": "application/json"
        }
        expected_data = "{}"

        actual_response = self.razor_client.post_data(test_path)

        T.assert_equal(expected_response, actual_response)
        self.mock_requests.post.assert_called_once_with(
            expected_path,
            headers=expected_headers,
            data=expected_data)

    def test_data(self):
        data = {
            "a": 1,
            "b": 2
        }
        expected_data = json.dumps(data)
        expected_headers = {
            "Content-Type": "application/json"
        }
        test_url = "http://%s:%s/irrelevant" % (self.hostname, self.port)

        self.razor_client.post_data(test_url, **data)
        self.mock_requests.post.assert_called_once_with(
            test_url,
            headers=expected_headers,
            data=expected_data)


class SanitizeCommandNameTest(RazorClientTestCase):

    def test_sanitizes_dashes(self):
        test_name = "something-with-dashes"
        expected_name = "something_with_dashes"
        actual_name = self.razor_client.sanitize_command_name(test_name)
        T.assert_equal(expected_name, actual_name)


class CoerceToFullUrlTest(RazorClientTestCase):

    def test_creates_full_path(self):
        test_path = "/api"
        expected_path = "http://%s:%s/api" % (self.hostname, self.port)
        actual_path = self.razor_client._coerce_to_full_url(test_path)
        T.assert_equal(expected_path, actual_path)

    def test_absolute_path_untouched(self):
        test_path = "http://%s:%s/api" % (self.hostname, self.port)
        expected_path = test_path
        actual_path = self.razor_client._coerce_to_full_url(test_path)
        T.assert_equal(expected_path, actual_path)


class MakeNetLocTest(RazorClientTestCase):

    def test_make_netloc(self):
        expected_host = "%s:%s" % (self.hostname, self.port)
        actual_host = self.razor_client._make_netloc()
        T.assert_equal(expected_host, actual_host)


class MakeRazorUrlTest(RazorClientTestCase):

    def test_make_razor_url(self):
        test_path = "/api"
        expected_path = "http://%s:%s/api" % (self.hostname, self.port)
        actual_path = self.razor_client._make_razor_url(test_path)
        T.assert_equal(expected_path, actual_path)


class BindCollectionTest(RazorClientTestCase):

    @T.setup_teardown
    def mock_list_collection(self):
        tgt = "py_razor_client.razor_client.RazorClient._list_collection"
        with mock.patch(tgt) as self.mock_list_collection:
            yield

    @T.setup_teardown
    def mock_get_collection_item(self):
        tgt = "py_razor_client.razor_client.RazorClient._get_collection_item"
        with mock.patch(tgt) as self.mock_get_collection_item:
            yield

    def test_bind_collection_vanilla(self):
        collection = "nodes"
        collection_id = "http://%s:%s/api/collections/%s" % (self.hostname,
                                                             self.port,
                                                             collection)
        test_collection = {
            "name": collection,
            "id": collection_id
        }
        expected_method = "nodes"
        expected_singular = "node"

        self.razor_client._bind_collection(test_collection)

        actual_method = getattr(self.razor_client, expected_method, None)
        actual_singular = getattr(self.razor_client, expected_singular, None)
        T.assert_not_equal(actual_method, None)
        T.assert_not_equal(actual_singular, None)

        actual_method()
        self.mock_list_collection.assert_called_once_with(collection_id)

        actual_singular()
        self.mock_get_collection_item.assert_called_once_with(collection_id)

    def test_bind_collection_replaces_policy_singular(self):
        collection = "policies"
        collection_id = "http://%s:%s/api/collections/%s" % (self.hostname,
                                                             self.port,
                                                             collection)
        test_collection = {
            "name": collection,
            "id": collection_id
        }
        expected_method = "policies"
        expected_singular = "policy"

        self.razor_client._bind_collection(test_collection)

        actual_method = getattr(self.razor_client, expected_method, None)
        actual_singular = getattr(self.razor_client, expected_singular, None)
        T.assert_not_equal(actual_method, None)
        T.assert_not_equal(actual_singular, None)

        actual_method()
        self.mock_list_collection.assert_called_once_with(collection_id)

        actual_singular()
        self.mock_get_collection_item.assert_called_once_with(collection_id)


class BindCommandTest(RazorClientTestCase):

    @T.setup_teardown
    def mock_list_collection(self):
        tgt = "py_razor_client.razor_client.RazorClient._execute_command"
        with mock.patch(tgt) as self.mock_execute_command:
            yield

    def test_bind_command(self):
        command = "unbind-node"
        command_id = "http://%s:%s/api/collections/%s" % (self.hostname,
                                                          self.port,
                                                          command)
        test_command = {
            "name": command,
            "id": command_id
        }
        expected_command_name = "unbind_node"

        self.razor_client._bind_command(test_command)

        actual_method = getattr(self.razor_client, expected_command_name, None)
        T.assert_not_equal(actual_method, None)

        actual_method()
        self.mock_execute_command.assert_called_once_with(command_id)


class BindMethodTest(RazorClientTestCase):

    def test_bind_method(self):
        test_method = lambda: None
        test_method_name = "test"
        expected_method = test_method

        self.razor_client._bind_method(test_method_name, test_method)

        actual_method = getattr(self.razor_client, test_method_name, None)
        T.assert_equal(expected_method, actual_method)


class GetListCollectionTest(RazorClientTestCase):

    @T.setup_teardown
    def mock_get_path(self):
        with mock.patch.object(self.razor_client, "get_path") as mock_get_path:
            self.mock_get_path = mock_get_path
            yield

    def test_list_collection(self):
        test_url = mock.sentinel.url
        self.razor_client._list_collection(test_url)
        self.mock_get_path.assert_called_once_with(test_url)

    def test_get_collection_item(self):
        test_url = "/api"
        test_item = "item"
        self.razor_client._get_collection_item(test_url, test_item)

        expected_url = "/".join((test_url, test_item))

        self.mock_get_path.assert_called_once_with(expected_url)


class ExecuteCommandTest(RazorClientTestCase):

    @T.setup_teardown
    def mock_post_data(self):
        with mock.patch.object(self.razor_client, "post_data") as mock_pd:
            self.mock_post_data = mock_pd
            yield

    def test_execute_command(self):
        url = mock.sentinel.url
        args = {
            "a": mock.sentinel.a,
            "b": mock.sentinel.b
        }
        self.razor_client._execute_command(url, **args)
        self.mock_post_data.assert_called_once_with(url, **args)

    def test_execute_command_transforms_args(self):
        url = mock.sentinel.url
        args = {
            "a": mock.sentinel.a,
            "iso_url": mock.sentinel.b
        }
        expected_args = {
            "a": mock.sentinel.a,
            "iso-url": mock.sentinel.b
        }
        self.razor_client._execute_command(url, **args)
        self.mock_post_data.assert_called_once_with(url, **expected_args)
