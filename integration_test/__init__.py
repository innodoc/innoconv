"""
Integration tests for innoconv.

These tests run the innoconv CLI and inspect its results.
"""

from os.path import dirname, join, realpath
from random import choices
from shutil import copytree, ignore_patterns
import string
from tempfile import TemporaryDirectory
from unittest import TestCase

REPO_DIR = join(dirname(realpath(__file__)), "tub_base")


class BaseConversionTest(TestCase):
    """Create a temporary directory for conversion."""

    def setUp(self):
        """Prepare temp dirs."""
        self.tmp_dir = TemporaryDirectory(prefix="innoconv-test-")
        self.output_dir = join(self.tmp_dir.name, "innoconv_output")

    def tearDown(self):
        """Clean up temp dirs."""
        self.tmp_dir.cleanup()

    def _copy_repo(self, ignore=None):
        """Create a copy of the content repository."""
        ignore = ignore if callable(ignore) else ignore_patterns(*ignore)
        rand = "".join(choices(string.ascii_lowercase + string.digits, k=8))
        repo_copy_dir = join(self.tmp_dir.name, "repo-copy-{}".format(rand))
        copytree(REPO_DIR, repo_copy_dir, ignore=ignore)
        return repo_copy_dir
