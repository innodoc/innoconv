"""Integration tests for conversion process using entry-point innoconv."""

# pylint: disable=missing-docstring,invalid-name

import io
import unittest
import unittest.mock
import filecmp
import os

from innoconv.__main__ import main  # noqa: F401
from integration_test.fixtures.handler import FixturesHandler

fixtures = FixturesHandler()


class TestConversionLocalFixtures(unittest.TestCase):

    def setUp(self):
        fixtures.prepare_fixtures()

    def tearDown(self):
        fixtures.cleanup_fixtures()

    def test_conversion(self):
        """A conversion should run without problems."""
        main(['-l', 'de',
              '-m', 'maketoc',
              '-m', 'squish',
              '-m', 'cpystatic',
              '-m', 'makemanifest',
              '-o', fixtures.TARGET,
              fixtures.SOURCE])
        self._tree_compare(fixtures.TARGET, fixtures.ORIGINAL_EXPECTED)

    def test_conversion_fail(self):
        """A conversion can fail."""
        with self.assertRaises(SystemExit):
            main(['-l', 'de',
                  '-m', 'maketoc',
                  '-m', 'squish',
                  '-m', 'cpystatic',
                  '-m', 'makemanifest',
                  '-o', fixtures.TARGET])

    @unittest.mock.patch('sys.stderr', new_callable=io.StringIO)
    def test_conversion_fail2(self, mock_stderr):
        """A conversion can fail."""
        self.assertEqual(1, main(['-l', 'en',
                                  '-d',
                                  '-m', 'maketoc',
                                  '-m', 'squish',
                                  '-m', 'cpystatic',
                                  '-m', 'makemanifest',
                                  '-o', fixtures.TARGET,
                                  fixtures.SOURCE]))
        self.assertTrue('Something went wrong' in mock_stderr.getvalue())

    def _tree_compare(self, dir1, dir2):
        dirs_cmp = filecmp.dircmp(dir1, dir2)
        if dirs_cmp.left_only or dirs_cmp.right_only or \
           dirs_cmp.funny_files:
            print('left_only', dirs_cmp.left_only)
            print('right_only', dirs_cmp.right_only)
            print('funny_files', dirs_cmp.funny_files)
            self.fail('left, right or funny')
        _, __, errors = filecmp.cmpfiles(
            dir1, dir2, dirs_cmp.common_files, shallow=False)
        if errors:
            print('errors', errors)
            self.fail('mismatch or errors')
        for common_dir in dirs_cmp.common_dirs:
            new_dir1 = os.path.join(dir1, common_dir)
            new_dir2 = os.path.join(dir2, common_dir)
            if not self._tree_compare(new_dir1, new_dir2):
                self.fail('Subdirs not equal')
        return True
