import unittest
import os
import panflute as pf
from mintmod_filter.utils import pandoc_parse, destringify

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

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
        "parse_pandoc() returns valid output if given test document"
        with open(os.path.join(SCRIPT_DIR, 'files', 'test.tex'), 'r') as f:
            content = f.read()
        doc = pandoc_parse(content)
        h1 = doc[0]
        para1 = doc[1]
        h2 = doc[2]
        para2 = doc[3]

        content_test = (
            (type(h1), pf.Header),
            (type(h1), pf.Header),
            (type(h1.content[0]), pf.Str),
            (h1.content[0].text, 'Test'),
            (type(h1.content[1]), pf.Space),
            (type(h1.content[2]), pf.Str),
            (h1.content[2].text, 'heading'),
            (h1.content[2].text, 'heading'),
            (type(para1), pf.Para),
            (len(para1.content), 121),
            (type(h2), pf.Header),
            (h2.content[0].text, 'Another'),
            (type(para1), pf.Para),
            (len(para2.content), 149),
        )

        for c in content_test:
            self.assertEqual(c[0], c[1])

    def test_parse_pandoc_empty(self):
        "parse_pandoc() returns [] if given empty document"
        ret = pandoc_parse('')
        self.assertEqual(ret, [])

    @unittest.skip("We need to write a second filter for label / index / ..."
                   "before this test will succeed, as subprocess cannot easily"
                   "the other processe's data")
    def test_parse_pandoc_mlabel(self):
        """Test if a latex string containing several `MLabel` commands in
        different environments and positions are parsed correctly.
        """
        ast_native = pandoc_parse(TEX_MLABEL)

        self.assertIsInstance(ast_native, list)

        header1 = ast_native[0]
        self.assertIsInstance(header1, pf.Header)
        self.assertEqual(header1.identifier, "label1")

        header2 = ast_native[1]
        self.assertIsInstance(header2, pf.Header)
        self.assertEqual(header2.identifier, "label2")

        header3 = ast_native[2].content[0]
        self.assertIsInstance(header3, pf.Header)
        self.assertEqual(header3.identifier, "LABEL_BASE_SITE_ONE")

        # para1 = ast_native[2]
        # self.assertIsInstance(para1, pf.Para)
        # self.assertEqual(para1.identifier, "paralabel")

    def test_destringify(self):
        str = 'This is a  really\tnice    string.'
        comp = [
            pf.Str('This'),
            pf.Space(),
            pf.Str('is'),
            pf.Space(),
            pf.Str('a'),
            pf.Space(),
            pf.Str('really'),
            pf.Space(),
            pf.Str('nice'),
            pf.Space(),
            pf.Str('string.'),
        ]
        ret = destringify(str)
        self.assertIsInstance(ret, list)
        self._compare_list(ret, comp)
        # for i, token in enumerate(ret):
        #     _type = type(comp[i])
        #     self.assertIsInstance(token, _type)
        #     if _type == pf.Str:
        #         self.assertEqual(token.text, comp[i].text)

    def test_destringify_empty(self):
        str = ''
        ret = destringify(str)
        self.assertIsInstance(ret, list)
        self.assertListEqual(ret, [])

    def test_destringify_empty_whitespace(self):
        str = '   '
        ret = destringify(str)
        self.assertIsInstance(ret, list)
        self.assertListEqual(ret, [])

    def test_destringify_one_word(self):
        str = 'foobar'
        ret = destringify(str)
        self.assertIsInstance(ret, list)
        self._compare_list(ret, [pf.Str('foobar')])

    def test_destringify_leading_trailing_whitespace(self):
        str = '  foo bar  '
        comp = [pf.Str('foo'), pf.Space(), pf.Str('bar')]
        ret = destringify(str)
        self.assertIsInstance(ret, list)
        self._compare_list(ret, comp)

    def _compare_list(self, l1, l2):
        for i, l1_elem in enumerate(l1):
            _type = type(l2[i])
            self.assertIsInstance(l1_elem, _type)
            if _type == pf.Str:
                self.assertEqual(l1_elem.text, l2[i].text)
