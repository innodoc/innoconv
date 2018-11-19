"""Unit tests for innoconv.__main__"""

# pylint: disable=missing-docstring

import unittest
from argparse import ArgumentParser, Namespace
from copy import deepcopy
import mock

import innoconv.__main__
from innoconv.extensions.abstract import AbstractExtension

DEFAULT_ARGS = {
    'debug': True,
    'source_dir': '/tmp/foo_source',
    'output_dir': '/tmp/bar_output',
    'languages': 'ar,it',
    'extensions': 'copystatic',
}


class TestGetArgs(unittest.TestCase):
    def test_get_arg_parser(self):
        args = innoconv.__main__.get_arg_parser()
        self.assertIsInstance(args, ArgumentParser)


@mock.patch('argparse.ArgumentParser.parse_args',
            return_value=Namespace(**DEFAULT_ARGS))
@mock.patch('innoconv.__main__.InnoconvRunner.__init__', return_value=None)
@mock.patch('innoconv.__main__.InnoconvRunner.run')
@mock.patch('innoconv.__main__.log')
class TestMain(unittest.TestCase):
    def test_main(self, log, runner_run, runner_init, _):
        return_value = innoconv.__main__.main()
        self.assertEqual(return_value, 0)
        args, kwargs = runner_init.call_args
        [source_dir, output_dir, [lang_0, lang_1], [extensions]] = args
        self.assertEqual(source_dir, '/tmp/foo_source')
        self.assertEqual(output_dir, '/tmp/bar_output')
        self.assertEqual(lang_0, 'ar')
        self.assertEqual(lang_1, 'it')
        self.assertIsInstance(extensions, AbstractExtension)
        self.assertEqual(kwargs, {'debug': True})
        self.assertTrue(runner_run.called)
        self.assertEqual(log.call_args, mock.call('Build finished!'))

    def test_main_invalid_ext(self, log, runner_run, runner_init, parse_args):
        args = deepcopy(DEFAULT_ARGS)
        args['extensions'] = 'copystatic,extension_does_not_exist'
        parse_args.return_value = Namespace(**args)
        return_value = innoconv.__main__.main()
        self.assertEqual(return_value, 1)
        self.assertFalse(runner_init.called)
        self.assertFalse(runner_run.called)
        err = ("Something went wrong: "
               "Extension extension_does_not_exist not found!")
        self.assertEqual(log.call_args, mock.call(err))

    def test_main_logs_error(self, log, runner_run, runner_init, _):
        runner_run.side_effect = RuntimeError('Oooops')
        return_value = innoconv.__main__.main()
        self.assertEqual(return_value, 1)
        self.assertTrue(runner_init.called)
        err = 'Something went wrong: Oooops'
        self.assertEqual(log.call_args, mock.call(err))


class TestMainInit(unittest.TestCase):

    @mock.patch('sys.exit')
    @mock.patch.object(innoconv.__main__, '__name__', '__main__')
    @mock.patch('innoconv.__main__.main')
    def test_main_init(self, main, sys_exit):
        main.return_value = 19
        innoconv.__main__.init()
        self.assertEqual(sys_exit.call_args[0][0], 19)
