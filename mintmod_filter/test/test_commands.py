# pylint: disable=missing-docstring

import unittest
import panflute as pf
from mintmod_filter.commands import Commands


class TestCommands(unittest.TestCase):

    def setUp(self):
        self.commands = Commands()

    def test_handle_msection(self):
        doc = pf.Doc(pf.RawBlock(r'\MSection{A Test Title}'), format='latex')
        elem = doc.content[0]  # this sets up elem.parent
        ret = self.commands.handle_msection(["A Test Title"])

        self.assertEqual(ret, [])

        last_header_elem = getattr(doc, "last_header_elem")

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
        doc = pf.Doc(pf.RawBlock(r'\MSRef{fooid}{linktext}'), format='latex')
        elem = doc.content[0]  # this sets up elem.parent
        ret = self.commands.handle_msref(['fooid', 'linktext'])
        self.assertIsInstance(ret, pf.Link)
        self.assertIsInstance(ret.content[0], pf.Str)
        self.assertEqual(ret.content[0].text, 'linktext')
        self.assertEqual(ret.url, '#fooid')
