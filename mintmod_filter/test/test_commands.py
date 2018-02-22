# pylint: disable=missing-docstring

import unittest
import panflute as pf
from mintmod_filter.commands import Commands


class TestCommands(unittest.TestCase):

    def setUp(self):
        self.doc = pf.Doc()
        self.commands = Commands()
        self.commands.doc = self.doc

    def test_handle_msection(self):
        ret = self.commands.handle_msection(["A Test Title"], None)

        self.assertEqual(ret, [])

        last_header_elem = getattr(self.doc, "last_header_elem", None)

        self.assertIsInstance(last_header_elem, pf.Header)
        self.assertIsInstance(last_header_elem.content[0], pf.Str)
        self.assertEqual(last_header_elem.content[0].text, 'A')
        self.assertIsInstance(last_header_elem.content[1], pf.Space)
        self.assertIsInstance(last_header_elem.content[2], pf.Str)
        self.assertEqual(last_header_elem.content[2].text, 'Test')
        self.assertIsInstance(last_header_elem.content[4], pf.Str)
        self.assertEqual(last_header_elem.content[4].text, 'Title')
        self.assertEqual(last_header_elem.identifier, "a-test-title")
        self.assertEqual(last_header_elem.level, 2)

    def test_handle_msref(self):
        ret = self.commands.handle_msref(['fooid', 'linktext'], None)
        self.assertIsInstance(ret, pf.Link)
        self.assertEqual(ret.content[0].text, 'linktext')
        self.assertEqual(ret.url, '#fooid')
