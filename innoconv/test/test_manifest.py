"""Unit tests for innoconv.modules.makemanifest"""

# pylint: disable=missing-docstring

import os
import unittest

from innoconv.modules.makemanifest.makemanifest import Makemanifest
from innoconv.constants import (MANIFEST_FILENAME,
                                STATIC_FOLDER,
                                CONTENT_FILENAME,
                                MANIFEST_YAML_FILENAME)

# supress linting until tests are implemented
# pylint: disable=W0611

EMPTY_MANIFEST_STRUCTURE = {
    'languages': [],
    'title': {},
    'toc': []
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
    os.path.join('en', '02 B'): 'artisan'
}

COMPELTE_MANIFEST_STRUCTURE = {
    'languages': ['la', 'en'],
    'title': {
        'la': 'L. Ipsum',
        'en': 'U. yr'
    },
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
    ]
}

MANIFEST_YAML_FILE = """
languages:
- la
- en
title:
    la: L. Ipsum
    en: U. yr

"""

MANIFEST_YAML = {
    'languages': [
        'la',
        'en'
    ],
    'title': {
        'la': 'L. Ipsum',
        'en': 'U. yr'
    }
}


def walk_side_effect_static(path):
    if STATIC_FOLDER not in path:
        return iter([('', [], [])])
    return iter([
        (STATIC_FOLDER, [])
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

        self.assertEqual(self.make_manifest.paths['output'],
                         'A')
        self.assertEqual(self.make_manifest.files['output'],
                         os.path.join('A', MANIFEST_FILENAME))
        self.assertEqual(self.make_manifest.paths['source'],
                         'B')
        self.assertEqual(self.make_manifest.files['source'],
                         os.path.join('B', MANIFEST_YAML_FILENAME))

    @unittest.mock.patch('os.path.isfile', return_value=True)
    def _set_yaml(self, *_):

        mock_open = unittest.mock.mock_open()
        with unittest.mock.patch('builtins.open', mock_open, create=True):
            with unittest.mock.patch('innoconv.modules.'
                                     'makemanifest.makemanifest.load',
                                     create=True) as mock_yaml:
                mock_yaml.return_value = MANIFEST_YAML
                self.make_manifest.load_manifest_yaml()

    def _make_toc(self):
        self._set_yaml()
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

    @unittest.mock.patch('os.path.isfile', return_value=True)
    def test_load_yaml(self, mock_isfile):
        self.assertEqual(self.make_manifest.get_languages(), [])
        self.assertEqual(self.make_manifest.get_title(), {})
        mock_open = unittest.mock.mock_open(
            read_data=MANIFEST_YAML_FILE
        )
        with unittest.mock.patch('builtins.open', mock_open, create=True):
            self.make_manifest.load_manifest_yaml()
        self.assertEqual(self.make_manifest.get_languages(),
                         MANIFEST_YAML['languages'])
        self.assertEqual(self.make_manifest.get_title(),
                         MANIFEST_YAML['title'])
        self.assertTrue(mock_open.called)
        self.assertTrue(mock_isfile.called)

    @unittest.mock.patch('os.path.isfile', return_value=False)
    def test_load_empty_yaml(self, mock_isfile):

        with self.assertRaises(RuntimeError):
            self.make_manifest.load_manifest_yaml()
        self.assertTrue(mock_isfile.called)

        mock_isfile.return_value = True
        # Test empty manifest
        mock_open = unittest.mock.mock_open(
            read_data=""
        )
        with unittest.mock.patch('builtins.open', mock_open, create=True):
            with self.assertRaises(RuntimeError):
                self.make_manifest.load_manifest_yaml()

        # Test no language block
        mock_open = unittest.mock.mock_open(
            read_data="""
            foo:
            - bar
            """
        )
        with unittest.mock.patch('builtins.open', mock_open, create=True):
            with self.assertRaises(RuntimeError):
                self.make_manifest.load_manifest_yaml()

        # Test no title block
        mock_open = unittest.mock.mock_open(
            read_data="""
            languages:
            - de
            """
        )
        with unittest.mock.patch('builtins.open', mock_open, create=True):
            with self.assertRaises(RuntimeError):
                self.make_manifest.load_manifest_yaml()

        # Test no title not defined for language
        mock_open = unittest.mock.mock_open(
            read_data="""
            languages:
            - de
            title:
                en: foo
            """
        )
        with unittest.mock.patch('builtins.open', mock_open, create=True):
            with self.assertRaises(RuntimeError):
                self.make_manifest.load_manifest_yaml()

        self.assertTrue(mock_open.called)
        self.assertTrue(mock_isfile.called)

    def test_make_toc(self):
        self._make_toc()
        self.assertEqual(self.make_manifest.get_toc(),
                         COMPELTE_MANIFEST_STRUCTURE['toc'])

    @unittest.mock.patch('os.path.isfile', return_value=True)
    def test_load_languages(self, isfile_mock):
        languages_source = ['blibb']
        languages = languages_source[:]
        mock_open = unittest.mock.mock_open()
        with unittest.mock.patch('builtins.open', mock_open, create=True):
            with unittest.mock.patch('innoconv.modules.'
                                     'makemanifest.makemanifest.load',
                                     create=True) as mock_yaml:
                mock_yaml.return_value = MANIFEST_YAML
                self.assertEqual(languages, languages_source)
                self.assertEqual(self.make_manifest.get_languages(), [])
                self.make_manifest.load_languages(languages)
                self.assertEqual(self.make_manifest.get_languages(),
                                 COMPELTE_MANIFEST_STRUCTURE['languages'])
                self.assertEqual(languages,
                                 COMPELTE_MANIFEST_STRUCTURE['languages'])
                self.assertTrue(isfile_mock)

    def test_title(self):
        self._make_toc()
        self.assertEqual(self.make_manifest.get_title(),
                         COMPELTE_MANIFEST_STRUCTURE['title'])

    @unittest.mock.patch('builtins.open')
    @unittest.mock.patch('os.path.isfile', return_value=True)
    @unittest.mock.patch('os.path.isdir', return_value=True)
    @unittest.mock.patch('os.listdir', side_effect=listdir_side_effect_pages)
    @unittest.mock.patch('json.dump')
    def test_compelte_cycle(self, json_mock, *_):
        self._initialize('', '')
        self._make_toc()
        self.make_manifest.post_conversion()
        self.assertEqual(self.make_manifest.manifest,
                         COMPELTE_MANIFEST_STRUCTURE)
        self.assertTrue(json_mock.called)
