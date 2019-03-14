"""Integration tests for error conditions in conversion process."""

# pylint: disable=missing-docstring

import unittest
from subprocess import call, PIPE
from os.path import join
import tempfile


class TestConversionFails(unittest.TestCase):
    def setUp(self):
        self.repo_dir = tempfile.TemporaryDirectory(prefix='innoconv-test-')
        self.output_dir = join(self.repo_dir.name, 'output_dir')

    def test_dir_does_not_exist(self):
        """A conversion should fail on non-existent directory."""
        non_existent_dir = join('dir', 'does', 'not', 'exist')
        command = ['innoconv', '-o', self.output_dir, non_existent_dir]
        returncode = call(command, timeout=60, stdout=PIPE, stderr=PIPE)
        self.assertNotEqual(returncode, 0)

    @unittest.skip('TODO')
    def test_langs_not_identical(self):
        # a conversion should fail if folder tree for languages is not
        # the same
        pass

    def tearDown(self):
        self.repo_dir.cleanup()
