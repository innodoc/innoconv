"""Unit tests for innoconv.modules.maketoc"""

# pylint: disable=missing-docstring

import unittest

import os

# supress linting until tests are implemented
# pylint: disable=W0611,invalid-name

from innoconv.modules.maketoc.maketoc import Maketoc

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

SOURCE = "SOURCE"
TARGET = "TARGET"

RESULT_TOC = [{'id': '01 A',
               'title': 'A',
               'children': [{'id': '01 A',
                             'title': 'AA'}]},
              {'id': '02 B',
               'title': 'BB',
               'children': [{'id': '02 B',
                             'title': 'B'}]},
              {'id': '03 C',
               'title': 'C'},
              {'id': '04 D',
               'title': 'DD',
               'children': [{'id': '04 D',
                             'title': 'DD'}]}]


class TestMaketoc(unittest.TestCase):

    def __init__(self, arg):
        super(TestMaketoc, self).__init__(arg)
        self.make_tok = Maketoc()

    def setUp(self):
        self.make_tok = Maketoc()

    @unittest.mock.patch('json.dump')
    @unittest.mock.patch('builtins.open')
    def test_maketoc(self, *args):
        json_mock = args[-1]
        self.make_tok.output_dir_base = TARGET
        self.make_tok.language = 'de'
        self.make_tok.tree = []
        self.make_tok.title = 'A'
        self.make_tok.rel_path = 'de' + os.sep + '01 A'
        self.make_tok.post_content_file()
        self.make_tok.title = 'AA'
        self.make_tok.rel_path = 'de' + os.sep + '01 A' + os.sep + '01 A'
        self.make_tok.post_content_file()
        self.make_tok.title = 'BB'
        self.make_tok.rel_path = 'de' + os.sep + '02 B'
        self.make_tok.post_content_file()
        self.make_tok.title = 'B'
        self.make_tok.rel_path = 'de' + os.sep + '02 B' + os.sep + '02 B'
        self.make_tok.post_content_file()
        self.make_tok.title = 'C'
        self.make_tok.rel_path = 'de' + os.sep + '03 C'
        self.make_tok.post_content_file()
        self.make_tok.title = 'DD'
        self.make_tok.rel_path = 'de' + os.sep + '04 D'
        self.make_tok.post_content_file()
        self.make_tok.title = 'DD'
        self.make_tok.rel_path = 'de' + os.sep + '04 D' + os.sep + '04 D'
        self.make_tok.post_content_file()

        self.assertFalse(json_mock.called)
        self.make_tok.post_language()
        self.assertTrue(json_mock.called)
        self.assertEqual(self.make_tok.tree, RESULT_TOC)

    def test_pre_content_file(self):
        self.make_tok.rel_path = "C"
        self.make_tok.full_path = "D"
        self.make_tok.pre_content_file('A', 'B')
        self.assertEqual(self.make_tok.rel_path, "A")
        self.assertEqual(self.make_tok.full_path, "B")

    def test_pre_language(self):
        self.make_tok.language = "B"
        self.make_tok.tree = {'A': 'B'}
        self.make_tok.pre_language('A')
        self.assertEqual(self.make_tok.language, "A")
        self.assertEqual(self.make_tok.tree, [])

    def test_pre_conversion(self):
        self.make_tok.output_dir_base = "B"
        self.make_tok.pre_conversion({'output': 'A'})
        self.assertEqual(self.make_tok.output_dir_base, "A")

    def test_processast(self):
        with self.assertRaises(ValueError):
            self.make_tok.process_ast({})
        with self.assertRaises(ValueError):
            self.make_tok.process_ast({'meta': {}})
        with self.assertRaises(ValueError):
            self.make_tok.process_ast({'meta': {'title': {}}})
        self.make_tok.title = "B"
        self.make_tok.process_ast({'meta': {'title': {'c': 'A'}}})
        self.assertEqual(self.make_tok.title, "A")
