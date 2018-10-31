"""Unit tests for innoconv.__main__"""

# pylint: disable=missing-docstring

from argparse import ArgumentParser, Namespace
import unittest
import mock

import innoconv.__main__


class TestGetArgParser(unittest.TestCase):

    def setUp(self):
        self.arg_parser = innoconv.__main__.get_arg_parser()

    def test_get_arg_parser(self):
        self.assertIsInstance(self.arg_parser, ArgumentParser)


class TestMain(unittest.TestCase):

    def setUp(self):
        get_arg_parser_patcher = mock.patch('innoconv.__main__.get_arg_parser')
        get_arg_parser_mock = get_arg_parser_patcher.start()
        arg_parser_mock = mock.Mock()
        attrs = {
            'parse_args.return_value': Namespace(
                debug=True,
                source_dir='/tmp/foo_source',
                output_dir_base='/tmp/bar_output',
                module=[],
            ),
        }
        arg_parser_mock.configure_mock(**attrs)
        get_arg_parser_mock.return_value = arg_parser_mock

        runner_init_patcher = mock.patch(
            'innoconv.__main__.InnoconvRunner.__init__')
        self.runner_init_mock = runner_init_patcher.start()
        self.runner_init_mock.return_value = None

        runner_run_patcher = mock.patch(
            'innoconv.__main__.InnoconvRunner.run')
        self.runner_run_mock = runner_run_patcher.start()

        log_patcher = mock.patch('innoconv.__main__.log')
        self.log_mock = log_patcher.start()

        self.addCleanup(mock.patch.stopall)

    def test_main(self):
        return_value = innoconv.__main__.main()
        args, kwargs = self.runner_init_mock.call_args
        self.assertEqual(
            args, ('/tmp/foo_source', '/tmp/bar_output', []))
        self.assertEqual(kwargs, {'debug': True})
        self.assertTrue(self.runner_run_mock.called)
        args, _ = self.log_mock.call_args
        self.assertEqual(return_value, 0)
        self.assertEqual(args, ('Build finished!',))

    def test_main_gives_error(self):
        self.runner_run_mock.side_effect = RuntimeError('Oooops')
        return_value = innoconv.__main__.main()
        self.assertEqual(return_value, 1)
        args, _ = self.log_mock.call_args
        self.assertEqual(args, ('Something went wrong: Oooops',))


class TestMainInit(unittest.TestCase):

    @mock.patch('sys.exit')
    @mock.patch.object(innoconv.__main__, '__name__', '__main__')
    @mock.patch('innoconv.__main__.main')
    def test_main_init(self, main_mock, sys_exit_mock):
        main_mock.return_value = 19
        innoconv.__main__.init()
        self.assertEqual(sys_exit_mock.call_args[0][0], 19)
