import unittest
import panflute as pf
from mintmod_filter.environments import Environments, MINFO_CLASSES


class TestEnvironments(unittest.TestCase):

    def setUp(self):
        self.environments = Environments()
        self.doc = pf.Doc()

    def test_handle_minfo(self):
        """Test if handle_minfo returns a Div with header and child
        env content"""
        elem_content = r"""\begin{itemize}
        \item{item1}
        \item{item2}
        \end{itemize}"""

        div = self.environments.handle_minfo(elem_content, [], self.doc)
        self.assertIsInstance(div, pf.Div)
        self.assertEquals(div.classes, MINFO_CLASSES)

        self.assertIsInstance(div.content[0], pf.Header)
        self.assertEquals(div.content[0].identifier, "")

        self.assertEquals(div.content[0].content[0].text, "Info")

        # is the env content parsed correctly?
        self.assertIsInstance(div.content[1], pf.BulletList)
        self.assertEquals(div.content[1].content[0].content[0]
                             .content[0].content[0].text, "item1")

        # TODO set and test a unique identifier to info boxes (and others)
