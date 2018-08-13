"""Integration tests for conversion process using entry-point innoconv."""

# pylint: disable=missing-docstring,invalid-name

import unittest
from subprocess import run, PIPE
import os
import tempfile
from git import Repo

REPO_URL = 'https://gitlab.tubit.tu-berlin.de/innodoc/tub_base.git'
REPO_BRANCH = 'innoconv'


class TestConversion(unittest.TestCase):

    def setUp(self):
        self.repo_dir = tempfile.TemporaryDirectory(prefix='innoconv-test-')
        self.repo = Repo.clone_from(
            REPO_URL, self.repo_dir.name, branch=REPO_BRANCH)
        self.output_dir = os.path.join(self.repo_dir.name, 'output_dir_base')

    def test_conversion(self):
        """A conversion should run without problems."""
        command = ['innoconv', '-o', self.output_dir, self.repo_dir.name]
        job = run(command, timeout=60, stdout=PIPE, stderr=PIPE)
        run(['find', self.output_dir])
        self.assertEqual(job.returncode, 0)

    def test_conversion_fail_dir_does_not_exist(self):
        """A conversion should fail on non-existent directory."""
        non_existent_dir = os.path.join('dir', 'does', 'not', 'exist')
        command = ['innoconv', '-o', self.output_dir, non_existent_dir]
        job = run(command, timeout=60, stdout=PIPE, stderr=PIPE)
        self.assertNotEqual(job.returncode, 0)

    def tearDown(self):
        self.repo_dir.cleanup()
