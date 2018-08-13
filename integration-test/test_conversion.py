"""Integration tests for conversion process using entry-point innoconv."""

# pylint: disable=missing-docstring,invalid-name

import unittest
from subprocess import run, PIPE
from os.path import isdir, join
import tempfile
from git import Repo

REPO_URL = 'https://gitlab.tubit.tu-berlin.de/innodoc/tub_base.git'
REPO_BRANCH = 'innoconv'


class TestConversion(unittest.TestCase):

    def setUp(self):
        self.repo_dir = tempfile.TemporaryDirectory(prefix='innoconv-test-')
        self.repo = Repo.clone_from(
            REPO_URL, self.repo_dir.name, branch=REPO_BRANCH)
        self.output_dir = join(self.repo_dir.name, 'output_dir_base')

    def test_conversion(self):
        """A conversion should run without problems."""
        command = ['innoconv', '-o', self.output_dir, self.repo_dir.name]
        job = run(command, timeout=60, stdout=PIPE, stderr=PIPE)
        self.assertEqual(job.returncode, 0)
        for lang in ('de', 'en'):
            self.assertTrue(isdir(join(self.output_dir, lang)))
            self.assertTrue(isdir(join(self.output_dir, lang, '01-project')))
            self.assertTrue(isdir(join(self.output_dir, lang, '02-elements')))
        # TODO: check existence and validity of some output files?

    def test_conversion_fail_dir_does_not_exist(self):
        """A conversion should fail on non-existent directory."""
        non_existent_dir = join('dir', 'does', 'not', 'exist')
        command = ['innoconv', '-o', self.output_dir, non_existent_dir]
        job = run(command, timeout=60, stdout=PIPE, stderr=PIPE)
        self.assertNotEqual(job.returncode, 0)

    @unittest.skip('TODO')
    def test_conversion_fail_langs_not_identical(self):
        # a conversion should fail if folder tree for languages is not
        # the same
        pass

    def tearDown(self):
        self.repo_dir.cleanup()
