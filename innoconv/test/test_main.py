"""Unit tests for innoconv.__main__"""

# pylint: disable=missing-docstring

import unittest
from argparse import ArgumentParser, Namespace
import mock

import innoconv.__main__
from innoconv.test.utils import get_manifest

DEFAULT_ARGS = {
    'debug': True,
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


@mock.patch('builtins.open', new_callable=mock.mock_open)
@mock.patch('innoconv.__main__.Manifest.from_yaml', return_value=MANIFEST)
@mock.patch('argparse.ArgumentParser.parse_args',
            return_value=Namespace(**DEFAULT_ARGS))
@mock.patch('innoconv.__main__.InnoconvRunner.__init__', return_value=None)
@mock.patch('innoconv.__main__.InnoconvRunner.run')
@mock.patch('innoconv.__main__.log')
class TestMain(unittest.TestCase):
    def test_main(self, log, runner_run, runner_init, *_):
        return_value = innoconv.__main__.main()
        self.assertEqual(return_value, 0)
        args, _ = runner_init.call_args
        source_dir, output_dir, manifest, (extension,) = args
        self.assertEqual(source_dir, '/tmp/foo_source')
        self.assertEqual(output_dir, '/tmp/bar_output')
        self.assertIs(manifest, MANIFEST)
        self.assertEqual(extension, 'copy_static')
        self.assertTrue(runner_run.called)
        self.assertEqual(log.call_args, mock.call('Build finished!'))

    def test_main_logs_error(self, log, runner_run, runner_init, *_):
        runner_run.side_effect = RuntimeError('Oooops')
        return_value = innoconv.__main__.main()
        self.assertEqual(return_value, 1)
        self.assertTrue(runner_init.called)
        err = 'Something went wrong: Oooops'
        self.assertEqual(log.call_args, mock.call(err))

    def test_main_no_manifest(self, *args):
        _, _, _, _, _, mock_open = args
        mock_open.side_effect = FileNotFoundError()
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
    @mock.patch('sys.exit')
    @mock.patch.object(innoconv.__main__, '__name__', '__main__')
    @mock.patch('innoconv.__main__.main')
    def test_main_init(self, main, sys_exit):
        main.return_value = 19
        innoconv.__main__.init()
        self.assertEqual(sys_exit.call_args[0][0], 19)
