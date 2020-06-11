"""Unit tests for the innoconv command-line interface."""

import logging
from os.path import join, realpath
import unittest
from unittest.mock import call, patch

from click.testing import CliRunner
from yaml import YAMLError

from innoconv.cli import cli
from innoconv.constants import DEFAULT_EXTENSIONS, LOG_FORMAT
from innoconv.manifest import Manifest


MANIFEST = Manifest(data={"title": "Foo title", "languages": ["en"], "min_score": 80})


@patch("innoconv.cli.Manifest.from_directory", side_effect=(MANIFEST,))
@patch("os.path.exists", return_value=False)
@patch("innoconv.cli.InnoconvRunner.run")
@patch("innoconv.cli.InnoconvRunner.__init__", return_value=None)
@patch("innoconv.cli.coloredlogs.install")
class TestCLI(unittest.TestCase):
    """Test the command-line interface argument parsing."""

    def test_help(self, *_):
        """Test the help argument."""
        runner = CliRunner()
        result = runner.invoke(cli, "--help")
        self.assertIs(result.exit_code, 0)
        self.assertIn("Usage: ", result.output)

    def test_defaults(self, coloredlogs_install, runner_init, run, *__):
        """Test the default arguments."""
        runner = CliRunner()
        result = runner.invoke(cli, ".")
        self.assertEqual(
            coloredlogs_install.call_args_list,
            [call(level=logging.WARNING, fmt=LOG_FORMAT)],
        )
        self.assertEqual(
            runner_init.call_args,
            call(
                realpath("."),
                realpath(join(".", "innoconv_output")),
                MANIFEST,
                list(DEFAULT_EXTENSIONS),
            ),
        )
        self.assertEqual(run.call_args_list, [call()])
        self.assertIs(result.exit_code, 0)

    def test_verbose(self, coloredlogs_install, *_):
        """Test the verbose flag."""
        runner = CliRunner()
        result = runner.invoke(cli, "--verbose .")
        self.assertIs(result.exit_code, 0)
        self.assertEqual(
            coloredlogs_install.call_args_list,
            [call(level=logging.INFO, fmt=LOG_FORMAT)],
        )

    def test_custom_outputdir(self, _, runner_init, *__):
        """Test the custom output directory argument."""
        runner = CliRunner()
        result = runner.invoke(cli, "--output-dir ./my_custom_output_dir .")
        self.assertIs(result.exit_code, 0)
        self.assertEqual(
            runner_init.call_args,
            call(
                realpath("."),
                realpath(join(".", "my_custom_output_dir")),
                MANIFEST,
                list(DEFAULT_EXTENSIONS),
            ),
        )

    def test_outputdir_already_exists(self, _, __, ___, exists, *____):
        """Ensure output directory existance is checked."""
        exists.return_value = True
        runner = CliRunner()
        result = runner.invoke(cli, ".")
        self.assertIsNot(result.exit_code, 0)

    def test_outputdir_overwrite(self, _, __, ___, exists, *____):
        """Test force overwrite flag."""
        exists.return_value = True
        runner = CliRunner()
        result = runner.invoke(cli, "--force .")
        self.assertIs(result.exit_code, 0)

    def test_manifest_failures(self, _, __, ___, ____, manifest_from_dir):
        """Test failing with different errors for manifest loading."""
        for ext in (YAMLError, FileNotFoundError, RuntimeError):
            with self.subTest(ext):
                manifest_from_dir.side_effect = (ext,)
                runner = CliRunner()
                result = runner.invoke(cli, ".")
                self.assertIsNot(result.exit_code, 0)

    def test_extensions(self, _, runner_init, *__):
        """Test the custom extensions argument."""
        runner = CliRunner()
        result = runner.invoke(cli, "--extensions join_strings,copy_static .")
        self.assertIs(result.exit_code, 0)
        self.assertEqual(
            runner_init.call_args,
            call(
                realpath("."),
                realpath(join(".", "innoconv_output")),
                MANIFEST,
                ["join_strings", "copy_static"],
            ),
        )

    def test_unknown_extension(self, *_):
        """Ensure failure for non-existent extension."""
        runner = CliRunner()
        result = runner.invoke(cli, "--extensions bogus_extension .")
        self.assertIsNot(result.exit_code, 0)

    def test_innoconv_runner_failure(self, _, run, *__):
        """Test failing of innoconvRunner."""
        run.side_effect = (RuntimeError,)
        runner = CliRunner()
        result = runner.invoke(cli, ".")
        self.assertIsNot(result.exit_code, 0)
