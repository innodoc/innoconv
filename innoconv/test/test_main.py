"""Unit tests for innoconv.__main__"""

# pylint: disable=missing-docstring

from argparse import ArgumentParser, Namespace
import unittest
import mock

from innoconv.__main__ import get_arg_parser, main


class TestGetArgParser(unittest.TestCase):

    def setUp(self):
        self.arg_parser = get_arg_parser()

    def test_get_arg_parser(self):
        self.assertIsInstance(self.arg_parser, ArgumentParser)


class TestMain(unittest.TestCase):

    def setUp(self):
        get_arg_parser_patcher = mock.patch('innoconv.__main__.get_arg_parser')
        get_arg_parser_mock = get_arg_parser_patcher.start()
        arg_parser_mock = mock.Mock()
        attrs = {
            'parse_args.return_value': Namespace(
                debug=False,
                source_dir='/tmp/foo_source',
                output_dir_base='/tmp/bar_output',
                languages='ar,it',
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

        sys_exit_patcher = mock.patch('sys.exit')
        self.sys_exit_mock = sys_exit_patcher.start()

        self.addCleanup(mock.patch.stopall)

    def test_main(self):
        main()
        self.assertTrue(self.runner_init_mock.called)
        args, kwargs = self.runner_init_mock.call_args
        self.assertEqual(
            args, ('/tmp/foo_source', '/tmp/bar_output', ['ar', 'it']))
        self.assertEqual(kwargs, {'debug': False})
        self.assertTrue(self.runner_run_mock.called)
        self.assertFalse(self.sys_exit_mock.called)
        args, _ = self.log_mock.call_args
        self.assertEqual(args, ('Build finished!',))

    def test_main_gives_error(self):
        self.runner_run_mock.side_effect = RuntimeError('Oooops')
        main()
        self.assertTrue(self.sys_exit_mock.called)
        self.assertEqual(self.sys_exit_mock.call_args, ((1,),))
        args, _ = self.log_mock.call_args
        self.assertEqual(args, ('Something went wrong: Oooops',))
