"""Unit tests for innoconv.utils"""

# pylint: disable=missing-docstring

import unittest
import mock

from innoconv.utils import to_ast


class TestToAst(unittest.TestCase):

    @mock.patch('innoconv.utils.Popen')
    def test_to_ast(self, popen_mock):
        """to_ast() calls pandoc"""
        pandoc_output = ('{"blocks":[{"t":"Para","c":[]}],"meta":{"title":'
                         '{"t":"MetaInlines","c":[{"t":"Str","c":"Test"}]}}}')
        process_mock = mock.Mock()
        attrs = {
            'returncode': 0,
            'communicate.return_value': (pandoc_output.encode(), ''.encode()),
        }
        process_mock.configure_mock(**attrs)
        popen_mock.return_value = process_mock

        blocks, title = to_ast('/some/document.md')

        self.assertTrue(popen_mock.called)
        self.assertEqual(blocks, [{'t': 'Para', 'c': []}])
        self.assertEqual(title, [{'t': 'Str', 'c': 'Test'}])

    @mock.patch('innoconv.utils.Popen')
    def test_to_ast_fails_without_title(self, popen_mock):
        """to_ast() fails without a title"""
        pandoc_output = ('{"blocks":[{"t":"Para","c":[]}],"meta":{}}')
        process_mock = mock.Mock()
        attrs = {
            'returncode': 0,
            'communicate.return_value': (pandoc_output.encode(), ''.encode()),
        }
        process_mock.configure_mock(**attrs)
        popen_mock.return_value = process_mock

        with self.assertRaises(ValueError):
            to_ast('/some/document.md')

    @mock.patch('innoconv.utils.Popen')
    def test_to_ast_fails(self, popen_mock):
        """to_ast() calls pandoc with error"""
        process_mock = mock.Mock()
        attrs = {
            'returncode': 255,
            'communicate.return_value': (''.encode(), ''.encode()),
        }
        process_mock.configure_mock(**attrs)
        popen_mock.return_value = process_mock

        with self.assertRaises(RuntimeError):
            to_ast('/some/document.md')
