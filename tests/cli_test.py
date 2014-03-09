# -*- coding: utf-8 -*-
from argparse import ArgumentParser
from contextlib import contextmanager
import StringIO

import mock
import testify as T

from py_razor_client import cli


class DynamicizeArgParserTest(T.TestCase):

    def test_adds_unknown_opts(self):
        test_cli = "--valid_argument foo --new-argument bar".split(" ")
        parser = ArgumentParser()
        parser.add_argument("--valid_argument")

        test_args = ('--new-argument', )
        expected_args = (("valid_argument", "foo"),
                         ('new_argument', "bar"))
        expected_added_args = ["new_argument", ]

        parser, added_args = cli.dynamicize_argparser(parser, test_args)

        args = parser.parse_args(test_cli)
        for arg, value in expected_args:
            T.assert_equal(getattr(args, arg), value)

        T.assert_equal(added_args, expected_added_args)


class FilterForLongOptsTest(T.TestCase):

    def test_filters_longopts(self):
        test_opts = ("--something", "x", "--other", "y", "z", "dd")
        expected_opts = ("--something", "--other")
        actual_opts = cli.filter_for_longopts(test_opts)
        T.assert_equal(expected_opts, actual_opts)


class LoadConfigTest(T.TestCase):

    @contextmanager
    def mock_open(self, contents=""):
        open_mock = mock.mock_open(read_data=contents)
        with mock.patch("__builtin__.open", open_mock) as mock_open:
            yield mock_open

    @contextmanager
    def mock_os_path_exists(self, answers):
        with mock.patch("py_razor_client.cli.os.path.exists") as mock_exists:
            mock_exists.side_effect = lambda x: bool(answers[x])
            yield mock_exists

    def test_specify_file(self):
        mock_path = "/some/config/file"
        mock_config = "test_key: test_value"
        os_path_exists_answers = {mock_path: True}
        expected_config = {"test_key": "test_value"}

        with self.mock_os_path_exists(os_path_exists_answers) as mock_exists:
            with self.mock_open(mock_config) as mock_open:
                actual_config = cli.load_config(mock_path)

                mock_open.assert_called_once_with(mock_path)
                mock_exists.assert_called_once_with(mock_path)
                T.assert_equal(expected_config, actual_config)

    def test_nonexistent_file(self):
        mock_path = "/some/dne/file"
        os_path_exists_answers = {mock_path: False}
        with self.mock_os_path_exists(os_path_exists_answers) as mock_exists:
            with T.assert_raises(cli.NoSuchConfigFileException):
                cli.load_config(mock_path)
            mock_exists.assert_called_once_with(mock_path)

    def test_first_rc_file(self):
        mock_path = cli.RC_LOCATIONS[0]
        os_path_exists_answers = {mock_path: True}
        mock_config = "test_key: test_value"
        expected_config = {"test_key": "test_value"}

        with self.mock_os_path_exists(os_path_exists_answers) as mock_exists:
            with self.mock_open(mock_config) as mock_open:
                actual_config = cli.load_config(mock_path)

                mock_open.assert_called_once_with(mock_path)
                mock_exists.assert_called_once_with(mock_path)
                T.assert_equal(expected_config, actual_config)

    def test_rc_fallback(self):
        dne_mock_path = cli.RC_LOCATIONS[0]
        mock_path = cli.RC_LOCATIONS[1]
        os_path_exists_answers = {dne_mock_path: False, mock_path: True}
        mock_config = "test_key: test_value"
        expected_config = {"test_key": "test_value"}

        with self.mock_os_path_exists(os_path_exists_answers) as mock_exists:
            with self.mock_open(mock_config) as mock_open:
                actual_config = cli.load_config(mock_path)

                mock_open.assert_called_once_with(mock_path)
                mock_exists.assert_called_once_with(mock_path)
                T.assert_equal(expected_config, actual_config)

    def test_no_config(self):
        os_path_exists_answers = {}
        for loc in cli.RC_LOCATIONS:
            os_path_exists_answers[loc] = False

        expected_config = {}
        with self.mock_os_path_exists(os_path_exists_answers) as mock_exists:
            with self.mock_open() as mock_open:
                actual_config = cli.load_config()

                T.assert_equal(mock_open.call_count, 0)
                T.assert_equal(mock_exists.call_count, len(cli.RC_LOCATIONS))
                T.assert_equal(expected_config, actual_config)
