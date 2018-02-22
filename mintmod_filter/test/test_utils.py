# pylint: disable=missing-docstring

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


class TestParsePandoc(unittest.TestCase):

    def test_parse_pandoc(self):
        "parse_pandoc() returns valid output if given test document"
        with open(os.path.join(SCRIPT_DIR, 'files', 'test.tex'), 'r') as file:
            content = file.read()
        doc = pandoc_parse(content)
        h_1 = doc[0]
        para_1 = doc[1]
        h_2 = doc[2]
        para_2 = doc[3]

        content_test = (
            (type(h_1), pf.Header),
            (type(h_1), pf.Header),
            (type(h_1.content[0]), pf.Str),
            (h_1.content[0].text, 'Test'),
            (type(h_1.content[1]), pf.Space),
            (type(h_1.content[2]), pf.Str),
            (h_1.content[2].text, 'heading'),
            (h_1.content[2].text, 'heading'),
            (type(para_1), pf.Para),
            (len(para_1.content), 121),
            (type(h_2), pf.Header),
            (h_2.content[0].text, 'Another'),
            (type(para_1), pf.Para),
            (len(para_2.content), 149),
        )

        for elem in content_test:
            self.assertEqual(elem[0], elem[1])

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

        # para_1 = ast_native[2]
        # self.assertIsInstance(para_1, pf.Para)
        # self.assertEqual(para_1.identifier, "paralabel")


class TestDestringify(unittest.TestCase):

    def test_regular(self):
        string = 'This is a  really\tnice    string.'
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
        ret = destringify(string)
        self.assertIsInstance(ret, list)
        self._compare_list(ret, comp)
        # TODO
        # for i, token in enumerate(ret):
        #     _type = type(comp[i])
        #     self.assertIsInstance(token, _type)
        #     if _type == pf.Str:
        #         self.assertEqual(token.text, comp[i].text)

    def test_empty(self):
        string = ''
        ret = destringify(string)
        self.assertIsInstance(ret, list)
        self.assertListEqual(ret, [])

    def test_empty_whitespace(self):
        string = '   '
        ret = destringify(string)
        self.assertIsInstance(ret, list)
        self.assertListEqual(ret, [])

    def test_one_word(self):
        string = 'foobar'
        ret = destringify(string)
        self.assertIsInstance(ret, list)
        self._compare_list(ret, [pf.Str('foobar')])

    def test_whitespace(self):
        string = '  foo bar  '
        comp = [pf.Str('foo'), pf.Space(), pf.Str('bar')]
        ret = destringify(string)
        self.assertIsInstance(ret, list)
        self._compare_list(ret, comp)

    def _compare_list(self, l_1, l_2):
        for i, l_1_elem in enumerate(l_1):
            _type = type(l_2[i])
            self.assertIsInstance(l_1_elem, _type)
            if _type == pf.Str:
                self.assertEqual(l_1_elem.text, l_2[i].text)
