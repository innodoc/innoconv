"""Integration tests for conversion process using entry-point innoconv."""

# pylint: disable=missing-docstring

import unittest
from subprocess import run, PIPE
from os import walk, sep, remove
from os.path import isdir, join, isfile, realpath, dirname
import json
from tempfile import TemporaryDirectory
from innoconv.constants import (CONTENT_BASENAME, STATIC_FOLDER, TIKZ_FOLDER,
                                MANIFEST_BASENAME)

REPO_DIR = join(dirname(realpath(__file__)), 'tub_base')
EXTRA_FILE = join(REPO_DIR, 'de', STATIC_FOLDER, 'TESTFILE.txt')
OUTPUT_CONTENT_FILENAME = '{}.json'.format(CONTENT_BASENAME)
MANIFEST_FILENAME = '{}.json'.format(MANIFEST_BASENAME)


class TestConversionTubBase(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = TemporaryDirectory(prefix='innoconv-test-output-')
        self.output_dir = self.tmp_dir.name
        # Create an extra file that should not be present in output folder
        with open(EXTRA_FILE, 'w+') as file:
            file.write("lorem Ipsum")

    def tearDown(self):
        self.tmp_dir.cleanup()
        remove(EXTRA_FILE)

    def test_conversion(self):
        """A conversion should run without problems."""
        command = [
            'innoconv',
            '--verbose',
            '--output-dir', self.output_dir,
            REPO_DIR]
        job = run(command, timeout=60, stdout=PIPE, stderr=PIPE)
        stdout = job.stdout.decode('utf-8')
        stderr = job.stderr.decode('utf-8')
        if job.returncode != 0:
            print(stdout)
            print(stderr)
        self.assertEqual(job.returncode, 0)
        self._test_converted_folders_present()
        self._test_each_folder_has_content()
        self._test_verbose_output(stderr)
        with self.subTest(extension='write_manifest'):
            data = self._test_write_manifest(stderr)
        with self.subTest(extension='generate_toc'):
            self._test_generate_toc(data)
        with self.subTest(extension='join_strings'):
            self._test_content()
        with self.subTest(extension='copystatic'):
            self._test_copy_static(stderr)
        with self.subTest(extension='tikz2svg'):
            self._test_tikz2svg(stderr)

    def _test_converted_folders_present(self):
        for lang in ('de', 'en'):
            self.assertTrue(isdir(join(self.output_dir, lang)))
            self.assertTrue(isdir(join(self.output_dir, lang, '02-elements')))
            self.assertTrue(isdir(join(self.output_dir,
                                       lang,
                                       '02-elements',
                                       '01-headers')))
            self.assertTrue(isdir(join(self.output_dir, lang, '01-project')))

    def _test_each_folder_has_content(self):
        for lang in ('de', 'en'):
            for dir_names, _, file_list in walk(join(self.output_dir, lang)):
                skip = False
                for dir_name in dir_names.split(sep):
                    if dir_name.startswith('_'):
                        skip = True
                if not skip:
                    self.assertIn(OUTPUT_CONTENT_FILENAME, file_list)

    def _test_content(self):
        filepath = join(self.output_dir, 'de', OUTPUT_CONTENT_FILENAME)
        with open(filepath) as file:
            data = json.load(file)
            paragraph = data[0]
            self.assertEqual(paragraph['t'], 'Para')
            content = paragraph['c'][0]
            self.assertEqual(content['t'], 'Str')
            self.assertIn('Dies ist ein Beispiel-Kurs', content['c'])

    def _test_copy_static(self, stderr):
        self.assertTrue(isdir(join(self.output_dir, STATIC_FOLDER)))
        self.assertTrue(isdir(join(self.output_dir, STATIC_FOLDER, '_de')))
        self.assertTrue(isfile(join(self.output_dir,
                                    STATIC_FOLDER,
                                    '02-elements',
                                    '06-media',
                                    'adam.jpg')))
        self.assertTrue(isfile(join(self.output_dir,
                                    STATIC_FOLDER,
                                    '_de',
                                    '02-elements',
                                    '06-media',
                                    'lines.png')))
        self.assertTrue(isfile(join(self.output_dir,
                                    STATIC_FOLDER,
                                    '_en',
                                    '02-elements',
                                    '06-media',
                                    'lines.png')))
        self.assertTrue(isfile(join(self.output_dir,
                                    STATIC_FOLDER,
                                    'subfolder',
                                    'math.jpg')))
        self.assertFalse(
            isfile(join(self.output_dir, STATIC_FOLDER, 'flag.png')))
        self.assertFalse(
            isfile(
                join(self.output_dir, STATIC_FOLDER, '_de', 'TESTFILE.txt')))
        self.assertIn('7 files found', stderr)
        self.assertIn(
            join(
                self.output_dir,
                STATIC_FOLDER,
                '_en',
                '02-elements',
                '06-media',
                'lines.png'),
            stderr)

    def _test_verbose_output(self, stderr):
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

    def _test_tikz2svg(self, stderr):
        self.assertTrue(isdir(join(self.output_dir, STATIC_FOLDER,
                                   TIKZ_FOLDER)))
        self.assertTrue(isfile(
            join(self.output_dir,
                 STATIC_FOLDER,
                 TIKZ_FOLDER,
                 'tikz_9c1f20bd9eee016034295f4dfc9d4c48.svg')))
        self.assertIn('Compiling 3 TikZ images.', stderr)

    def _test_write_manifest(self, stderr):
        filepath = join(self.output_dir, MANIFEST_FILENAME)
        self.assertTrue(isfile(filepath))
        with open(filepath) as file:
            data = json.load(file)
            self.assertIn('languages', data)
            self.assertIn('de', data['languages'])
            self.assertIn('en', data['languages'])
            self.assertIn('title', data)
            self.assertIn('de', data['title'])
            self.assertIn('en', data['title'])
            self.assertEqual('innoDoc-Showcase-Kurs', data['title']['de'])
            self.assertEqual('innoDoc Showcase Course', data['title']['en'])
        self.assertIn('Wrote manifest', stderr)
        return data

    def _test_generate_toc(self, data):
        self.assertIn('toc', data)
        self.assertIn('title', data['toc'][0])
        self.assertIn('id', data['toc'][0])
        self.assertIn('children', data['toc'][0])
        self.assertEqual(4, len(data['toc'][0]['children']))
        self.assertEqual('01-project', data['toc'][0]['id'])
        self.assertIn('de', data['toc'][0]['title'])
        self.assertIn('en', data['toc'][0]['title'])
        self.assertEqual('Projektstruktur', data['toc'][0]['title']['de'])
        self.assertEqual('Project structure', data['toc'][0]['title']['en'])
