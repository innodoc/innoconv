"""Unit tests for innoconv.__main__"""

# pylint: disable=missing-docstring

import unittest
from unittest.mock import call, DEFAULT, mock_open, patch
from argparse import ArgumentParser, Namespace

import innoconv.__main__
from .utils import get_manifest

DEFAULT_ARGS = {
    'verbose': True,
    'source_dir': '/tmp/foo_source',
    'output_dir': '/tmp/bar_output',
    'languages': 'ar,it',
    'extensions': 'copy_static',
}

MANIFEST = get_manifest()


class TestGetArgs(unittest.TestCase):
    def test_get_arg_parser(self):
        args = innoconv.__main__.get_arg_parser()
        self.assertIsInstance(args, ArgumentParser)


@patch('builtins.open', new_callable=mock_open)
@patch('innoconv.__main__.Manifest.from_yaml', return_value=MANIFEST)
@patch('argparse.ArgumentParser.parse_args',
       return_value=Namespace(**DEFAULT_ARGS))
@patch('innoconv.__main__.InnoconvRunner.__init__', return_value=None)
@patch('innoconv.__main__.InnoconvRunner.run')
@patch.multiple('logging', info=DEFAULT, critical=DEFAULT)
class TestMain(unittest.TestCase):
    def test_main(self, runner_run, runner_init, *_, **logging):
        log = logging['info']
        return_value = innoconv.__main__.main()
        self.assertEqual(return_value, 0)
        args, _ = runner_init.call_args
        source_dir, output_dir, manifest, (extension,) = args
        self.assertEqual(source_dir, '/tmp/foo_source')
        self.assertEqual(output_dir, '/tmp/bar_output')
        self.assertIs(manifest, MANIFEST)
        self.assertEqual(extension, 'copy_static')
        self.assertTrue(runner_run.called)
        self.assertEqual(log.call_args, call('Build finished!'))

    def test_main_logs_error(self, runner_run, runner_init, *_, **logging):
        log = logging['critical']
        runner_run.side_effect = RuntimeError('Oooops')
        return_value = innoconv.__main__.main()
        self.assertEqual(return_value, 1)
        self.assertTrue(runner_init.called)
        err = 'Something went wrong: Oooops'
        self.assertEqual(log.call_args, call(err))

    def test_main_no_manifest(self, *args, **_):
        _, _, _, _, mocked_open = args
        mocked_open.side_effect = FileNotFoundError()
        return_value = innoconv.__main__.main()
        self.assertEqual(return_value, -2)

    def test_main_runtime_error(self, *args, **logging):
        log = logging['critical']
        _, _, _, manifest_from_yaml, _ = args
        manifest_from_yaml.side_effect = RuntimeError()
        return_value = innoconv.__main__.main()
        self.assertEqual(return_value, -3)
        self.assertIsInstance(log.call_args[0][0], RuntimeError)


class TestMainInit(unittest.TestCase):
    @patch('sys.exit')
    @patch.object(innoconv.__main__, '__name__', '__main__')
    @patch('innoconv.__main__.main')
    def test_main_init(self, main, sys_exit):
        main.return_value = 19
        innoconv.__main__.init()
        self.assertEqual(sys_exit.call_args[0][0], 19)
