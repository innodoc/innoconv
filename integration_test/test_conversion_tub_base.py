"""Integration tests for conversion process using entry-point innoconv."""

# pylint: disable=missing-docstring

import unittest
from subprocess import run, PIPE
from os import walk, sep, makedirs
from os.path import isdir, join, isfile
import json
import tempfile
from git import Repo
from innoconv.constants import OUTPUT_CONTENT_FILENAME, STATIC_FOLDER

REPO_URL = 'https://gitlab.tubit.tu-berlin.de/innodoc/tub_base.git'
REPO_BRANCH = 'master'


class TestConversionTubBase(unittest.TestCase):

    def setUp(self):
        self.repo_dir = tempfile.TemporaryDirectory(prefix='innoconv-test-')
        self.repo = Repo.clone_from(
            REPO_URL, self.repo_dir.name, branch=REPO_BRANCH)
        self.output_dir = join(self.repo_dir.name, 'output_dir_base')

    def _test_converted_folders_present(self):
        for lang in ('de', 'en'):
            self.assertTrue(isdir(join(self.output_dir, lang)))
            self.assertTrue(isdir(join(self.output_dir, lang, '02-elements')))
            self.assertTrue(isdir(join(self.output_dir,
                                       lang,
                                       '02-elements',
                                       '01-headers')))
        self.assertTrue(isdir(join(self.output_dir, 'de', '01 Home')))
        self.assertTrue(isdir(join(self.output_dir, 'en', '01-project')))

    def _test_each_folder_has_content(self):
        for lang in ('de', 'en'):
            for dir_names, _, file_list in walk(join(self.output_dir, lang)):
                skip = False
                for dir_name in dir_names.split(sep):
                    if dir_name.startswith('_'):
                        skip = True
                if not skip:
                    self.assertIn(OUTPUT_CONTENT_FILENAME, file_list)

    def _test_content_is_json(self):
        filepath = join(self.output_dir, 'de', OUTPUT_CONTENT_FILENAME)
        with open(filepath) as file:
            data = json.load(file)
            paragraph = data[0]
            self.assertEqual(paragraph['t'], 'Para')
            content = paragraph['c'][0]
            self.assertEqual(content['t'], 'Str')
            self.assertIn('Dies', content['c'])

    def _prepare_test_copystatic(self):
        path = join(
            self.output_dir,
            'de',
            STATIC_FOLDER,
            'TESTFILE.txt')
        makedirs(join(self.output_dir, 'de', STATIC_FOLDER))
        with open(path, "w+") as file:
            file.write("lorem Ipsum")

    def _test_copystatic(self, stderr):
        self.assertTrue(isdir(join(self.output_dir, STATIC_FOLDER)))
        self.assertTrue(isdir(join(self.output_dir, 'de', STATIC_FOLDER)))
        self.assertTrue(isfile(join(self.output_dir,
                                    STATIC_FOLDER,
                                    'adam.jpg')))
        self.assertTrue(isfile(join(self.output_dir,
                                    'de',
                                    STATIC_FOLDER,
                                    'flag.png')))
        self.assertTrue(isfile(join(self.output_dir,
                                    'de',
                                    STATIC_FOLDER,
                                    '02-elements',
                                    '06-images',
                                    'TU_Logo.png')))
        self.assertFalse(isfile(join(self.output_dir,
                                     STATIC_FOLDER,
                                     'flag.png')))
        self.assertFalse(isfile(join(self.output_dir,
                                     'de',
                                     STATIC_FOLDER,
                                     'TESTFILE.txt')))
        self.assertIn(
            ' copying file ',
            stderr)
        self.assertIn(
            join(
                self.output_dir,
                'de',
                STATIC_FOLDER,
                '02-elements',
                '06-images',
                'TU_Logo.png'),
            stderr)

    def _test_debug_output(self, stderr):
        self.assertIn(
            join(
                'de',
                '02-elements',
                '03-links-and-formatting',
                'content.json'),
            stderr)
        self.assertIn(
            join(
                'de',
                '02-elements',
                '04-quotes',
                'content.json'),
            stderr)
        self.assertIn(
            'Build finished!',
            stderr)

    def test_conversion(self):
        """A conversion should run without problems."""
        self._prepare_test_copystatic()
        command = [
            'innoconv', '-d', '-e', 'copystatic', '-o', self.output_dir,
            self.repo_dir.name]
        job = run(command, timeout=60, stdout=PIPE, stderr=PIPE)
        stdout = job.stdout.decode('utf-8')
        stderr = job.stderr.decode('utf-8')
        if job.returncode != 0:
            print(stdout)
            print(stderr)
        self.assertEqual(job.returncode, 0)
        self._test_converted_folders_present()
        self._test_each_folder_has_content()
        self._test_content_is_json()
        self._test_debug_output(stderr)
        self._test_copystatic(stderr)

    def tearDown(self):
        self.repo_dir.cleanup()
