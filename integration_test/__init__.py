"""
Integration tests for innoconv.

These tests run the innoconv CLI and inspect its results.
"""

from os.path import dirname, join, realpath
from random import choice
from shutil import copytree, ignore_patterns
from string import ascii_lowercase, digits
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
        rand = "".join(choice(ascii_lowercase + digits) for _ in range(8))
        repo_copy_dir = join(self.tmp_dir.name, f"repo-copy-{rand}")
        copytree(REPO_DIR, repo_copy_dir, ignore=ignore)
        return repo_copy_dir
