"""Unit tests for innoconv.modules.makemanifest"""

# pylint: disable=missing-docstring

import os
import unittest

from innoconv.modules.makemanifest.makemanifest import Makemanifest
from innoconv.constants import (MANIFEST_FILENAME,
                                STATIC_FOLDER,
                                CONTENT_FILENAME,
                                LICENSE_FOLDER,
                                LICENSE_FILENAME,
                                ABOUT_FOLDER,
                                ABOUT_FILENAME,
                                INSTITUTION_FOLDER,
                                INSTITUTION_FILENAME,
                                PAGES_FOLDER,
                                LOGO_FILENAME,
                                FAVICON_FILENAME,
                                GENERATE_PDF_FILENAME)

# supress linting until tests are implemented
# pylint: disable=W0611

EMPTY_MANIFEST_STRUCTURE = {
    'languages': [],
    'title': {},
    'logo': False,
    'favicon': False,
    'toc': [],
    'generate_pdf': False,
    'license': False,
    'about': False,
    'institution': False,
    'pages': {}
}

TITLES = {
    'la': 'Lorem Ipsum',
    os.path.join('la', '01 A'): 'Dolor',
    os.path.join('la', '01 A', '01 A1'): 'Sit',
    os.path.join('la', '01 A', '02 A2'): 'Amet',
    os.path.join('la', '01 A', '02 A2', '01 A1I'): 'Consectetur',
    os.path.join('la', '01 A', '03 A3'): 'Libero',
    os.path.join('la', '02 B'): 'Adipiscing',
    'en': 'Umami yr',
    os.path.join('en', '01 A'): 'farm-to-table',
    os.path.join('en', '01 A', '01 A1'): 'everyday',
    os.path.join('en', '01 A', '02 A2'): 'gluten-free',
    os.path.join('en', '01 A', '02 A2', '01 A1I'): 'tumblr',
    os.path.join('en', '01 A', '03 A3'): 'mixtape',
    os.path.join('en', '02 B'): 'artisan',
    os.path.join(STATIC_FOLDER, PAGES_FOLDER, 'la', 'ca'): 'Curabitur',
    os.path.join(STATIC_FOLDER, PAGES_FOLDER, 'la', 'qa'): 'Quam',
    os.path.join(STATIC_FOLDER, PAGES_FOLDER, 'en', 'ci'): 'pitchfork',
    os.path.join(STATIC_FOLDER, PAGES_FOLDER, 'en', 'qi'): 'semiotics',
    os.path.join(STATIC_FOLDER, PAGES_FOLDER, 'en', 'xi'): 'unicorn'
}

COMPELTE_MANIFEST_STRUCTURE = {
    'languages': ['la', 'en'],
    'title': {
        'la': 'Lorem Ipsum',
        'en': 'Umami yr'
    },
    'logo': True,
    'favicon': True,
    'toc': [
        {
            'id': '01 A',
            'title': {
                'la': 'Dolor',
                'en': 'farm-to-table'
            },
            'children': [
                {
                    'id': '01 A1',
                    'title': {
                        'la': 'Sit',
                        'en': 'everyday'
                    },
                    'children': []
                },
                {
                    'id': '02 A2',
                    'title': {
                        'la': 'Amet',
                        'en': 'gluten-free'
                    },
                    'children': [
                        {
                            'id': '01 A1I',
                            'title': {
                                'la': 'Consectetur',
                                'en': 'tumblr'
                            },
                            'children': []
                        }
                    ]
                },
                {
                    'id': '03 A3',
                    'title': {
                        'la': 'Libero',
                        'en': 'mixtape'
                    },
                    'children': []
                }
            ]
        },
        {
            'id': '02 B',
            'title': {
                'la': 'Adipiscing',
                'en': 'artisan'
            },
            'children': []
        }
    ],
    'generate_pdf': True,
    'license': True,
    'about': True,
    'institution': True,
    'pages': {
        'la': {
            'ca': 'Curabitur',
            'qa': 'Quam'
        },
        'en': {
            'ci': 'pitchfork',
            'qi': 'semiotics',
            'xi': 'unicorn'
        }
    }
}


def walk_side_effect_static(path):
    if STATIC_FOLDER not in path:
        return iter([('', [], [])])
    return iter([
        (STATIC_FOLDER, [LICENSE_FOLDER, ABOUT_FOLDER, INSTITUTION_FOLDER,
                         PAGES_FOLDER], [LOGO_FILENAME, FAVICON_FILENAME,
                                         GENERATE_PDF_FILENAME]),
        (os.path.join(STATIC_FOLDER, LICENSE_FOLDER),
         [],
         ['la' + LICENSE_FILENAME, 'en' + LICENSE_FILENAME]),
        (os.path.join(STATIC_FOLDER, ABOUT_FOLDER),
         [],
         ['la' + ABOUT_FILENAME, 'en' + ABOUT_FILENAME]),
        (os.path.join(STATIC_FOLDER, INSTITUTION_FOLDER),
         [],
         ['la' + INSTITUTION_FILENAME, 'en' + INSTITUTION_FILENAME]),
        (os.path.join(STATIC_FOLDER, PAGES_FOLDER),
         ['la', 'en'],
         []),
        (os.path.join(STATIC_FOLDER, PAGES_FOLDER, 'la'),
         [],
         ['ca', 'qa']),
        (os.path.join(STATIC_FOLDER, PAGES_FOLDER, 'en'),
         [],
         ['ci', 'qi', 'xi'])
    ])


def walk_side_effect_content(path):
    lang = path[-2:]
    return iter([
        (lang, ['01 A', '02 B'], [CONTENT_FILENAME]),
        (os.path.join(lang, '01 A'), ['01 A1', '02 A2', '03 A3'],
         [CONTENT_FILENAME]),
        (os.path.join(lang, '01 A', '01 A1'), [], [CONTENT_FILENAME]),
        (os.path.join(lang, '01 A', '02 A2'), ['01 A1I'], [CONTENT_FILENAME]),
        (os.path.join(lang, '01 A', '02 A2', '01 A1I'), [],
         [CONTENT_FILENAME]),
        (os.path.join(lang, '01 A', '03 A3'), [], [CONTENT_FILENAME]),
        (os.path.join(lang, '02 B'), [], [CONTENT_FILENAME])
    ])


def listdir_side_effect_pages(path):
    if "la" in path:
        return ['ca', 'qa']
    if "en" in path:
        return ['ci', 'qi', 'xi']
    return []


def get_ast(path):
    return {
        'blocks': ['content_ast'],
        'meta': {
            'title': {
                'c': TITLES[path]
            }
        }
    }


class TestGenerateManifest(unittest.TestCase):

    def __init__(self, arg):
        super(TestGenerateManifest, self).__init__(arg)
        self.make_manifest = None

    def setUp(self):
        self.make_manifest = Makemanifest()

    @unittest.mock.patch('json.dump')
    @unittest.mock.patch('builtins.open')
    def test_write_manifest(self, *args):
        json_mock = args[-1]
        self.assertFalse(json_mock.called)
        self.make_manifest.write_manifest()
        self.assertTrue(json_mock.called)

    def _initialize(self, source='B', target='A'):
        self.make_manifest.pre_conversion({
            'output': target,
            'source': source
        })

    def test_new_manifest(self):
        self._initialize()
        self.assertEqual(self.make_manifest.manifest, EMPTY_MANIFEST_STRUCTURE)

        self.assertEqual(self.make_manifest.output_path,
                         'A')
        self.assertEqual(self.make_manifest.output_filname,
                         os.path.join('A', MANIFEST_FILENAME))

        self.assertEqual(self.make_manifest.static_folder,
                         os.path.join('B', STATIC_FOLDER))

    @unittest.mock.patch('os.path.isdir', return_value=False)
    @unittest.mock.patch('os.path.isfile', return_value=False)
    def test_has_no_folders(self, isfilepatch, isdirpatch):
        self.make_manifest.pre_language('de')
        self.assertFalse(self.make_manifest.has_about())
        self.assertFalse(self.make_manifest.has_license())
        self.assertFalse(self.make_manifest.has_institution())
        self.assertTrue(isdirpatch.called)
        self.assertFalse(isfilepatch.called)

    @unittest.mock.patch('os.path.isdir', return_value=True)
    @unittest.mock.patch('os.path.isfile', return_value=False)
    def test_has_no_files(self, isfilepatch, isdirpatch):
        self.make_manifest.pre_language('de')
        self.assertFalse(self.make_manifest.has_about())
        self.assertFalse(self.make_manifest.has_license())
        self.assertFalse(self.make_manifest.has_institution())
        self.assertTrue(isdirpatch.called)
        self.assertTrue(isfilepatch.called)

    def _set_languages(self):
        self.make_manifest.pre_language('la')
        self.make_manifest.pre_language('en')

    @unittest.mock.patch('os.path.isdir', return_value=True)
    @unittest.mock.patch('os.path.isfile',
                         side_effect=(lambda f: f.startswith('la')))
    def test_has_too_few_files(self, isfilepatch, isdirpatch):
        self._set_languages()
        self.assertFalse(self.make_manifest.has_about())
        self.assertFalse(self.make_manifest.has_license())
        self.assertFalse(self.make_manifest.has_institution())
        self.assertTrue(isdirpatch.called)
        self.assertTrue(isfilepatch.called)

    @unittest.mock.patch('os.path.isdir', return_value=True)
    @unittest.mock.patch('os.path.isfile', return_value=True)
    def test_has_files_and_folders(self, isfilepatch, isdirpatch):
        self.make_manifest.pre_language('de')
        self.assertTrue(self.make_manifest.has_about())
        self.assertTrue(self.make_manifest.has_license())
        self.assertTrue(self.make_manifest.has_institution())
        self.assertTrue(isdirpatch.called)
        self.assertTrue(isfilepatch.called)

    @unittest.mock.patch('os.path.isdir',
                         side_effect=(lambda f: ABOUT_FOLDER in f))
    @unittest.mock.patch('os.path.isfile', return_value=True)
    def test_only_about(self, isfilepatch, isdirpatch):
        self._set_languages()
        self.assertTrue(self.make_manifest.has_about())
        self.assertFalse(self.make_manifest.has_license())
        self.assertFalse(self.make_manifest.has_institution())
        self.assertTrue(isdirpatch.called)
        self.assertTrue(isfilepatch.called)

    @unittest.mock.patch('os.path.isdir',
                         side_effect=(lambda f: LICENSE_FOLDER in f))
    @unittest.mock.patch('os.path.isfile', return_value=True)
    def test_only_license(self, isfilepatch, isdirpatch):
        self._set_languages()
        self.assertFalse(self.make_manifest.has_about())
        self.assertTrue(self.make_manifest.has_license())
        self.assertFalse(self.make_manifest.has_institution())
        self.assertTrue(isdirpatch.called)
        self.assertTrue(isfilepatch.called)

    @unittest.mock.patch('os.path.isdir',
                         side_effect=(lambda f: INSTITUTION_FOLDER in f))
    @unittest.mock.patch('os.path.isfile', return_value=True)
    def test_only_institution(self, isfilepatch, isdirpatch):
        self._set_languages()
        self.assertFalse(self.make_manifest.has_about())
        self.assertFalse(self.make_manifest.has_license())
        self.assertTrue(self.make_manifest.has_institution())
        self.assertTrue(isdirpatch.called)
        self.assertTrue(isfilepatch.called)

    def _make_toc(self):
        self._set_languages()
        for lang in self.make_manifest.get_languages():
            for path, _, __ in walk_side_effect_content(lang):
                self.make_manifest.pre_content_file(path, path)
                self.make_manifest.process_ast(get_ast(path))
                self.make_manifest.post_content_file()

    def test_process_ast(self):
        self.make_manifest.current_title = ""
        with self.assertRaises(ValueError):
            self.make_manifest.process_ast({})
        with self.assertRaises(ValueError):
            self.make_manifest.process_ast({'meta': {}})
        with self.assertRaises(ValueError):
            self.make_manifest.process_ast({'meta': {'title': {}}})
        self.assertEqual(self.make_manifest.current_title, "")
        self.make_manifest.process_ast({'meta': {'title': {'c': 'A'}}})
        self.assertEqual(self.make_manifest.current_title, "A")

    def test_make_toc(self):
        self._make_toc()
        self.assertEqual(self.make_manifest.get_toc(),
                         COMPELTE_MANIFEST_STRUCTURE['toc'])

    def test_title(self):
        self._make_toc()
        self.assertEqual(self.make_manifest.get_title(),
                         COMPELTE_MANIFEST_STRUCTURE['title'])

    def test_set_language(self):
        self.assertEqual(self.make_manifest.get_languages(),
                         [])
        self.make_manifest.pre_language('de')
        self.assertEqual(self.make_manifest.get_languages(),
                         ['de'])
        self.make_manifest.pre_language('en')
        self.assertEqual(self.make_manifest.get_languages(),
                         ['de', 'en'])

    @unittest.mock.patch('os.path.isfile', return_value=True)
    def test_has_logo(self, is_file_mock):
        self._initialize()
        self.assertTrue(self.make_manifest.has_logo())
        self.assertTrue(is_file_mock.called)
        is_file_mock.reset_mock()
        is_file_mock.return_value = False
        self.assertFalse(self.make_manifest.has_logo())
        self.assertTrue(is_file_mock.called)

    @unittest.mock.patch('os.path.isfile', return_value=True)
    def test_has_favicon(self, is_file_mock):
        self._initialize()
        self.assertTrue(self.make_manifest.has_favicon())
        self.assertTrue(is_file_mock.called)
        is_file_mock.reset_mock()
        is_file_mock.return_value = False
        self.assertFalse(self.make_manifest.has_favicon())
        self.assertTrue(is_file_mock.called)

    @unittest.mock.patch('os.path.isfile', return_value=True)
    def test_has_generate_pdf(self, is_file_mock):
        self._initialize()
        is_file_mock.reset_mock()
        self.assertTrue(self.make_manifest.has_generate_pdf())
        self.assertTrue(is_file_mock.called)
        is_file_mock.reset_mock()
        is_file_mock.return_value = False
        self.assertFalse(self.make_manifest.has_generate_pdf())
        self.assertTrue(is_file_mock.called)

    @unittest.mock.patch('os.path.isdir', return_value=False)
    def test_has_pages(self, os_path_isdir_mock):
        self._initialize()
        os_path_isdir_mock.reset_mock()
        self.assertFalse(self.make_manifest.has_pages())
        self.assertTrue(os_path_isdir_mock.called)
        os_path_isdir_mock.reset_mock()
        os_path_isdir_mock.return_value = True
        self.assertTrue(self.make_manifest.has_pages())
        self.assertTrue(os_path_isdir_mock.called)

    @unittest.mock.patch('os.listdir', side_effect=listdir_side_effect_pages)
    @unittest.mock.patch('innoconv.modules.makemanifest.makemanifest.to_ast',
                         side_effect=get_ast)
    def test_process_pages(self, to_ast_mock, os_listdir_mock):
        self._initialize('')
        self._set_languages()
        to_ast_mock.reset_mock()
        os_listdir_mock.reset_mock()
        self.make_manifest.process_pages()
        self.assertTrue(os_listdir_mock.called)
        self.assertTrue(to_ast_mock.called)
        self.assertEqual(self.make_manifest.get_pages(),
                         COMPELTE_MANIFEST_STRUCTURE['pages'])

    @unittest.mock.patch('builtins.open')
    @unittest.mock.patch('os.path.isfile', return_value=True)
    @unittest.mock.patch('os.path.isdir', return_value=True)
    @unittest.mock.patch('os.listdir', side_effect=listdir_side_effect_pages)
    @unittest.mock.patch('innoconv.modules.makemanifest.makemanifest.to_ast',
                         side_effect=get_ast)
    @unittest.mock.patch('json.dump')
    def test_compelte_cycle(self, json_mock, *_):
        self._initialize('', '')
        self._make_toc()
        self.make_manifest.post_conversion()
        self.assertEqual(self.make_manifest.manifest,
                         COMPELTE_MANIFEST_STRUCTURE)
        self.assertTrue(json_mock.called)
