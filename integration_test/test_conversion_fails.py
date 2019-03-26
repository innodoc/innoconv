"""Integration tests for error conditions in conversion process."""

from os.path import join
from subprocess import call, PIPE
import tempfile
import unittest


class TestConversionFails(unittest.TestCase):
    """Test a failing conversion."""

    def setUp(self):
        """Prepare temp dirs."""
        self.repo_dir = tempfile.TemporaryDirectory(prefix="innoconv-test-")
        self.output_dir = join(self.repo_dir.name, "output_dir")

    def tearDown(self):
        """Clean up temp dirs."""
        self.repo_dir.cleanup()

    def test_dir_does_not_exist(self):
        """A conversion should fail on non-existent directory."""
        non_existent_dir = join("dir", "does", "not", "exist")
        command = ["innoconv", "-o", self.output_dir, non_existent_dir]
        returncode = call(command, timeout=60, stdout=PIPE, stderr=PIPE)
        self.assertNotEqual(returncode, 0)

    # TODO: implement missing test
    @unittest.skip("TODO")
    def test_langs_not_identical(self):
        """A conversion should fail if folder tree does not reflect config."""
