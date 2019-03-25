"""Unit tests for innoconv.cli"""

# pylint: disable=missing-docstring

import unittest
from unittest.mock import call, patch
import logging
from os.path import join, realpath
from click.testing import CliRunner
from click import BadParameter

from innoconv.cli import cli
from innoconv.constants import DEFAULT_EXTENSIONS, LOG_FORMAT
from innoconv.manifest import Manifest


MANIFEST = Manifest(data={'title': 'Foo title', 'languages': ['en']})


@patch('innoconv.cli.Manifest.from_directory', side_effect=(MANIFEST,))
@patch('os.path.exists', return_value=False)
@patch('innoconv.cli.InnoconvRunner.run')
@patch('innoconv.cli.InnoconvRunner.__init__', return_value=None)
@patch('innoconv.cli.logging.basicConfig')
class TestCLI(unittest.TestCase):
    def test_help(self, *_):
        runner = CliRunner()
        result = runner.invoke(cli, '--help')
        self.assertIs(result.exit_code, 0)
        self.assertIn('Usage: ', result.output)

    def test_defaults(self, logging_basicconfig, runner_init, run, *__):
        runner = CliRunner()
        result = runner.invoke(cli, '.')
        self.assertEqual(logging_basicconfig.call_args_list,
                         [call(level=logging.WARNING, format=LOG_FORMAT)])
        self.assertEqual(
            runner_init.call_args,
            call(realpath('.'), realpath(join('.', 'innoconv_output')),
                 MANIFEST, list(DEFAULT_EXTENSIONS))
        )
        self.assertEqual(run.call_args_list, [call()])
        self.assertIs(result.exit_code, 0)

    def test_verbose(self, logging_basicconfig, *_):
        runner = CliRunner()
        result = runner.invoke(cli, '--verbose .')
        self.assertIs(result.exit_code, 0)
        self.assertEqual(logging_basicconfig.call_args_list,
                         [call(level=logging.INFO, format=LOG_FORMAT)])

    def test_custom_outputdir(self, _, runner_init, *__):
        runner = CliRunner()
        result = runner.invoke(cli, '--output-dir ./my_custom_output_dir .')
        self.assertIs(result.exit_code, 0)
        self.assertEqual(
            runner_init.call_args,
            call(realpath('.'), realpath(join('.', 'my_custom_output_dir')),
                 MANIFEST, list(DEFAULT_EXTENSIONS))
        )

    def test_outputdir_already_exists(self, _, __, ___, exists, *____):
        exists.return_value = True
        runner = CliRunner()
        result = runner.invoke(cli, '.')
        self.assertIsNot(result.exit_code, 0)

    def test_outputdir_overwrite(self, _, __, ___, exists, *____):
        exists.return_value = True
        runner = CliRunner()
        result = runner.invoke(cli, '--force .')
        self.assertIs(result.exit_code, 0)

    def test_extensions(self, _, runner_init, *__):
        runner = CliRunner()
        result = runner.invoke(cli, '--extensions join_strings,copy_static .')
        self.assertIs(result.exit_code, 0)
        self.assertEqual(
            runner_init.call_args,
            call(realpath('.'), realpath(join('.', 'innoconv_output')),
                 MANIFEST, ['join_strings', 'copy_static'])
        )
