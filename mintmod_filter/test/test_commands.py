import unittest
import panflute as pf
from mintmod_filter.commands import Commands


class TestCommands(unittest.TestCase):

    def setUp(self):
        self.commands = Commands()

    def test_handle_msection(self):
        doc = pf.Doc()
        ret = self.commands.handle_msection(["A Test Title"], None, doc)

        self.assertEquals(ret, [])

        last_header_elem = getattr(doc, "last_header_elem", None)

        self.assertIsInstance(last_header_elem, pf.Header)
        self.assertIsInstance(last_header_elem.content[0], pf.RawInline)
        self.assertEquals(last_header_elem.content[0].text, "A Test Title")
        self.assertEquals(last_header_elem.identifier, "a-test-title")
        self.assertEquals(last_header_elem.level, 2)
