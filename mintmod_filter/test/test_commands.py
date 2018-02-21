import unittest
import panflute as pf
from mintmod_filter.commands import Commands


class TestCommands(unittest.TestCase):

    def setUp(self):
        self.commands = Commands()
        self.doc = pf.Doc()

    def test_handle_msection(self):
        ret = self.commands.handle_msection(["A Test Title"], None, self.doc)

        self.assertEqual(ret, [])

        last_header_elem = getattr(self.doc, "last_header_elem", None)

        self.assertIsInstance(last_header_elem, pf.Header)
        self.assertIsInstance(last_header_elem.content[0], pf.RawInline)
        self.assertEqual(last_header_elem.content[0].text, "A Test Title")
        self.assertEqual(last_header_elem.identifier, "a-test-title")
        self.assertEqual(last_header_elem.level, 2)

    def test_handle_msref(self):
        ret = self.commands.handle_msref(['fooid', 'linktext'], None, self.doc)
        self.assertIsInstance(ret, pf.Link)
        self.assertEqual(ret.content[0].text, 'linktext')
        self.assertEqual(ret.url, '#fooid')
