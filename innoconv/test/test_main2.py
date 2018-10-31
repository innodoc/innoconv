"""Unit tests for innoconv.__main__"""

# pylint: disable=missing-docstring

import unittest

# supress linting until tests are implemented
# pylint: disable=W0611
from innoconv.constants import DEFAULT_OUTPUT_DIR_BASE
from innoconv.__main__ import get_arg_parser, main  # noqa: F401

DEFAULT_PARSED_ARGUMENTS = {
    'debug': False,
    'output_dir_base': DEFAULT_OUTPUT_DIR_BASE,
    'module': [],
    'source_dir': ''
}


class TestMain2(unittest.TestCase):

    def _test(self, arguments, expected):
        full_expected = DEFAULT_PARSED_ARGUMENTS.copy()
        full_expected.update(expected)
        result = vars(get_arg_parser().parse_args(arguments))
        self.assertEqual(full_expected, result)

    def test_parse_no_args(self):
        arguments = []
        expected = {}
        with self.assertRaises(SystemExit):
            self._test(arguments, expected)

    def test_parse_only_output_folder(self):
        arguments = ['test']
        expected = {'source_dir': 'test'}
        self._test(arguments, expected)

    def test_parse_output(self):
        arguments = ['-o', 'out', 'test']
        expected = {
            'source_dir': 'test',
            'output_dir_base': 'out'
        }
        self._test(arguments, expected)
        arguments = ['--output-dir-base', 'out', 'test']
        self._test(arguments, expected)

    def test_parse_debug(self):
        arguments = ['-d', 'test']
        expected = {
            'source_dir': 'test',
            'debug': True
        }
        self._test(arguments, expected)
        arguments = ['--debug', 'test']
        self._test(arguments, expected)

    def test_parse_module(self):
        arguments = ['-m', 'testm', 'test']
        expected = {
            'source_dir': 'test',
            'module': ['testm']
        }
        self._test(arguments, expected)
        arguments = ['--module', 'testm', 'test']
        self._test(arguments, expected)

    def test_parse_modules(self):
        arguments = ['-m', 'testm', '-m', 'testm2', 'test']
        expected = {
            'source_dir': 'test',
            'module': ['testm', 'testm2']
        }
        self._test(arguments, expected)
        arguments = ['--module', 'testm', '--module', 'testm2', 'test']
        self._test(arguments, expected)

    def test_main_noarg(self):
        with self.assertRaises(SystemExit):
            main([])

    def test_main_mod_error(self):
        self.assertEqual(1, main(['-m', 'blubb', 'test']))

    def test_main_mod(self):
        self.assertEqual(1, main(['-m', 'demo', 'test']))
