"""Integration tests for error conditions in conversion process."""

from os import mkdir
from os.path import join
from subprocess import call, PIPE

from click import FileError, UsageError

from innoconv.constants import EXIT_CODES
from . import BaseConversionTest, REPO_DIR


class TestConversionFailsNonExistingSource(BaseConversionTest):
    """Test a non-existing source directory."""

    def test_dir_does_not_exist(self):
        """A conversion should fail on non-existent directory."""
        non_existent_dir = join("dir", "does", "not", "exist")
        command = ["innoconv", "-o", self.output_dir, non_existent_dir]
        exit_code = call(command, timeout=60, stdout=PIPE, stderr=PIPE)
        self.assertEqual(exit_code, UsageError.exit_code)


class TestConversionFailsUnknownExtension(BaseConversionTest):
    """Test an unknown extension."""

    def test_unknown_extension(self):
        """A conversion should fail on an unknown extension."""
        command = [
            "innoconv",
            "-o",
            self.output_dir,
            "-e",
            "extension-does-not-exist",
            REPO_DIR,
        ]
        exit_code = call(command, timeout=60, stdout=PIPE, stderr=PIPE)
        self.assertEqual(exit_code, UsageError.exit_code)


class TestConversionFailOutputExists(BaseConversionTest):
    """Test a failing conversion for existing output directory."""

    def test_output_dir_exists(self):
        """A conversion should fail on existent output directory."""
        mkdir(self.output_dir)
        command = ["innoconv", "-o", self.output_dir, REPO_DIR]
        exit_code = call(command, timeout=60, stdout=PIPE, stderr=PIPE)
        self.assertEqual(exit_code, FileError.exit_code)


class TestConversionFailMissingManifest(BaseConversionTest):
    """Test a missing manifest."""

    def test_missing_manifest(self):
        """A conversion should fail on missing manifest file."""
        repo_copy = self._copy_repo(("manifest.yml",))
        command = ["innoconv", "-o", self.output_dir, repo_copy]
        exit_code = call(command, timeout=60, stdout=PIPE, stderr=PIPE)
        self.assertEqual(exit_code, EXIT_CODES["MANIFEST_ERROR"])


class TestConversionFailDirectoryStructure(BaseConversionTest):
    """
    Test detection of inconsistent content directory structure.

    A conversion should fail if content directory tree is not identical for all
    languages.
    """

    def test_inconsistent_folders(self):
        """A conversion should fail on inconsistent content directories."""

        def _ignore(path, _):
            if "en/02-elements/04-links/01-internal" in path:
                return ["content.md"]
            return []

        repo_copy = self._copy_repo(_ignore)
        command = ["innoconv", "-o", self.output_dir, repo_copy]
        exit_code = call(command, timeout=60, stdout=PIPE, stderr=PIPE)
        self.assertEqual(exit_code, EXIT_CODES["RUNNER_ERROR"])
