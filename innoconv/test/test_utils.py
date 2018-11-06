"""Unit tests for innoconv.utils"""

# pylint: disable=missing-docstring

import unittest
import mock

from innoconv.utils import to_ast, log, set_debug


class TestLog(unittest.TestCase):

    @mock.patch('sys.stderr.write')
    @mock.patch('sys.stderr.flush')
    def test_log(self, stderr_flush_mock, stderr_write_mock):
        set_debug(True)
        log('Foo bar')
        self.assertEqual(stderr_write_mock.call_count, 1)
        self.assertEqual(stderr_write_mock.call_args, (('Foo bar\n',),))
        self.assertEqual(stderr_flush_mock.call_count, 1)
        stderr_write_mock.reset_mock()
        stderr_flush_mock.reset_mock()
        set_debug(False)
        log('Foo bar')
        self.assertFalse(stderr_write_mock.called)
        self.assertFalse(stderr_flush_mock.called)
        stderr_write_mock.reset_mock()
        stderr_flush_mock.reset_mock()
        set_debug(True)
        log('Foo','bar')
        self.assertEqual(stderr_write_mock.call_count, 2)
        self.assertEqual(stderr_write_mock.call_args, (('bar\n',),))
        self.assertEqual(stderr_flush_mock.call_count, 1)


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
