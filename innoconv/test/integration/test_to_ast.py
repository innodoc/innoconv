"""Integration tests for util function to_ast(), tests pandoc output"""

# pylint: disable=missing-docstring,invalid-name

import os
import unittest

from innoconv.utils import to_ast

FIXTURES_DIR = '{}/fixtures'.format(
    os.path.dirname(os.path.realpath(__file__)))


class TestToAst(unittest.TestCase):

    def test_to_ast(self):
        """to_ast() returns AST if given test Markdown document"""

        blocks, title = to_ast('{}/test_valid.md'.format(FIXTURES_DIR))

        self.assertEqual(title[0], {'t': 'Str', 'c': 'Test'})
        self.assertEqual(title[1], {'t': 'Space'})
        self.assertEqual(title[2], {'t': 'Str', 'c': 'document'})

        self.assertEqual(len(blocks), 9)

        h1 = blocks[0]
        self.assertEqual(h1['t'], 'Header')
        self.assertEqual(h1['c'][0], 1)  # level
        self.assertEqual(h1['c'][1][0], 'section-1-10-words')  # id
        self.assertEqual(len(h1['c'][2]), 7)

        p1 = blocks[1]
        self.assertEqual(p1['t'], 'Para')
        self.assertEqual(len(p1['c']), 19)

        h1_1 = blocks[2]
        self.assertEqual(h1_1['t'], 'Header')
        self.assertEqual(h1_1['c'][0], 2)
        self.assertEqual(h1_1['c'][1][0], 'section-1.1-50-words')
        self.assertEqual(len(h1_1['c'][2]), 7)

        p1_1 = blocks[3]
        self.assertEqual(p1_1['t'], 'Para')
        self.assertEqual(len(p1_1['c']), 99)

        h2 = blocks[4]
        self.assertEqual(h2['t'], 'Header')
        self.assertEqual(h2['c'][0], 1)
        self.assertEqual(h2['c'][1][0], 'section-2-8-words')
        self.assertEqual(len(h2['c'][2]), 7)

        p2a = blocks[5]
        self.assertEqual(p2a['t'], 'Para')
        self.assertEqual(len(p2a['c']), 15)

        h2_2 = blocks[6]
        self.assertEqual(h2_2['t'], 'Header')
        self.assertEqual(h2_2['c'][0], 2)
        self.assertEqual(h2_2['c'][1][0], 'section-2.1-20-words')
        self.assertEqual(len(h2_2['c'][2]), 7)

        p2a = blocks[7]
        self.assertEqual(p2a['t'], 'Para')
        self.assertEqual(len(p2a['c']), 39)

        p2b = blocks[8]
        self.assertEqual(p2b['t'], 'Para')
        self.assertEqual(len(p2b['c']), 1)
        link = p2b['c'][0]
        self.assertEqual(link['t'], 'Link')
        self.assertEqual(link['c'][1][0]['c'], 'Wikipedia')
