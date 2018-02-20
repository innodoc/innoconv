import unittest
import panflute as pf
from mintmod_filter.utils import pandoc_parse

TEX_MLABEL = r"""\MSubSection{foo}
\MLabel{label1}

\MTitle{header level 4}
\MLabel{label2}

\begin{MXContent}{Die erste Seite}{Seite 1}{STD}
\MLabel{LABEL_BASE_SITE_ONE}

Here is a text with another \MLabel{paralabel}
\end{MXContent}"""


class TestUtils(unittest.TestCase):

    def test_parse_pandoc(self):
        pass

    def test_parse_pandoc_mlabel(self):
        """Test if a latex string containing several `MLabel` commands in
        different environments and positions are parsed correctly.
        """
        ast_native = pandoc_parse(TEX_MLABEL)

        self.assertIsInstance(ast_native, list)

        header1 = ast_native[0]
        self.assertIsInstance(header1, pf.Header)
        self.assertEquals(header1.identifier, "label1")

        header2 = ast_native[1]
        self.assertIsInstance(header2, pf.Header)
        self.assertEquals(header2.identifier, "label2")

        header3 = ast_native[2].content[0]
        self.assertIsInstance(header3, pf.Header)
        self.assertEquals(header3.identifier, "LABEL_BASE_SITE_ONE")

        # para1 = ast_native[2]
        # self.assertIsInstance(para1, pf.Para)
        # self.assertEquals(para1.identifier, "paralabel")
