"""Unit tests for innoconv.modules.makemanifest"""

# pylint: disable=missing-docstring

import os
import unittest

from innoconv.modules.makemanifest.makemanifest import Makemanifest
from innoconv.constants import (MANIFEST_FILENAME,
                                STATIC_FOLDER,
                                CONTENT_FILENAME)

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
        'la': 'Lorem Ipsum',
        'en': 'Umami yr'
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

        self.assertEqual(self.make_manifest.output_path,
                         'A')
        self.assertEqual(self.make_manifest.output_filname,
                         os.path.join('A', MANIFEST_FILENAME))

        self.assertEqual(self.make_manifest.static_folder,
                         os.path.join('B', STATIC_FOLDER))

    def _set_languages(self):
        self.make_manifest.manifest['languages'] = ['la', 'en']

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

    def test_load_yaml(self):
        self.assertEqual(self.make_manifest.get_languages(), [])
        self.assertEqual(self.make_manifest.get_title(), {})
        mock_open = unittest.mock.mock_open(
            read_data=MANIFEST_YAML_FILE
        )
        # read_data=MANIFEST_YAML_FILE
        with unittest.mock.patch('builtins.open', mock_open, create=True):
            self.make_manifest.load_manifest_yaml()
        self.assertEqual(self.make_manifest.get_languages(),
                         MANIFEST_YAML['languages'])
        self.assertEqual(self.make_manifest.get_title(),
                         MANIFEST_YAML['title'])
        self.assertTrue(mock_open.called)

    def test_make_toc(self):
        self._make_toc()
        self.assertEqual(self.make_manifest.get_toc(),
                         COMPELTE_MANIFEST_STRUCTURE['toc'])

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
