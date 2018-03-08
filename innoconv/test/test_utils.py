# pylint: disable=missing-docstring,invalid-name

import unittest
import os
from mock import patch
import panflute as pf

from innoconv.errors import ParseError
from innoconv.utils import parse_fragment, destringify, parse_cmd
from innoconv.test.utils import captured_output

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

TEX_MLABEL = r"""\MSubSection{foo}
\MLabel{label1}

\MTitle{header level 4}
\MLabel{label2}

\begin{MXContent}{Die erste Seite}{Seite 1}{STD}
\MLabel{LABEL_BASE_SITE_ONE}

Here is a text with another \MLabel{paralabel}
\end{MXContent}"""


class TestParseFragment(unittest.TestCase):

    def test_parse_fragment(self):
        """parse_fragment() returns valid output if given test document"""
        with open(os.path.join(SCRIPT_DIR, 'files', 'test.tex'), 'r') as file:
            content = file.read()
        doc = parse_fragment(content)
        h_1 = doc[0]
        para_1 = doc[1]
        h_2 = doc[2]
        para_2 = doc[3]

        # test types
        type_tests = (
            (h_1, pf.Header),
            (h_1, pf.Header),
            (h_1.content[0], pf.Str),
            (h_1.content[1], pf.Space),
            (h_1.content[2], pf.Str),
            (para_1, pf.Para),
            (h_2, pf.Header),
            (para_1, pf.Para),
        )
        for elem in type_tests:
            with self.subTest(_type=type(elem[0])):
                self.assertIsInstance(elem[0], elem[1])

        # test content
        content_tests = (
            (h_1.content[0].text, 'Test'),
            (h_1.content[2].text, 'heading'),
            (len(para_1.content), 121),
            (h_2.content[0].text, 'Another'),
            (h_2.content[2].text, 'heading'),
            (len(para_2.content), 149),
        )
        for elem in content_tests:
            with self.subTest(value=elem[0]):
                self.assertEqual(elem[0], elem[1])

    def test_parse_fragment_fail(self):
        """if given broken document parse_fragment() should return [] and print
        errors"""
        with captured_output() as out:
            ret = parse_fragment(r'\begin{fooenv}bla')
            err_out = out[1].getvalue()
        self.assertTrue('ERROR' in err_out)
        self.assertListEqual(ret, [])

    def test_parse_fragment_quiet(self):
        """parse_fragment() prints debug messages"""
        with captured_output() as out:
            parse_fragment(r'\section{foo} \unknownfoobar')
            err_out = out[1].getvalue()
        self.assertTrue('Could not handle command unknownfoobar' in err_out)

    @patch('innoconv.utils.log')
    def test_parse_fragment_log_is_called(self, log_mock):
        """parse_fragment() calls log function on warning"""
        parse_fragment(r'\unknowncommandfoobar')
        self.assertTrue(log_mock.called)

    def test_parse_fragment_empty(self):
        """parse_fragment() returns [] if given empty document"""
        ret = parse_fragment('')
        self.assertEqual(ret, [])

    @patch('innoconv.utils.which', return_value=None)
    def test_parse_fragment_not_in_path(self, mock_func):
        # pylint: disable=unused-argument
        """parse_fragment() raises OSError if panzer not in PATH"""
        with self.assertRaises(OSError):
            parse_fragment('foo bar')

    # TODO: should be moved to integration tests
    @unittest.skip("We need to write a second filter for label / index / ..."
                   "before this test will succeed, as subprocess cannot easily"
                   "the other processe's data")
    def test_parse_fragment_mlabel(self):
        """Test if a latex string containing several `MLabel` commands in
        different environments and positions are parsed correctly."""
        ast_native = parse_fragment(TEX_MLABEL)

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
        """Test destringify with a regular string"""
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

    def test_empty(self):
        """Test destringify with an empty string"""
        string = ''
        ret = destringify(string)
        self.assertIsInstance(ret, list)
        self.assertListEqual(ret, [])

    def test_empty_whitespace(self):
        """Test destringify with an whitespace string"""
        string = '   '
        ret = destringify(string)
        self.assertIsInstance(ret, list)
        self.assertListEqual(ret, [])

    def test_one_word(self):
        """Test destringify with one word"""
        string = 'foobar'
        ret = destringify(string)
        self.assertIsInstance(ret, list)
        self._compare_list(ret, [pf.Str('foobar')])

    def test_whitespace(self):
        """Test destringify with leading and trailing whitespace"""
        string = '  foo bar  '
        comp = [pf.Str('foo'), pf.Space(), pf.Str('bar')]
        ret = destringify(string)
        self.assertIsInstance(ret, list)
        self._compare_list(ret, comp)

    def _compare_list(self, l_1, l_2):
        for i, l_1_elem in enumerate(l_1):
            _type = type(l_2[i])
            with self.subTest(i=i):
                with self.subTest(_type=_type):
                    self.assertIsInstance(l_1_elem, _type)
                if _type == pf.Str:
                    with self.subTest(text=l_1_elem.text):
                        self.assertEqual(l_1_elem.text, l_2[i].text)


class TestParseCmd(unittest.TestCase):

    def test_parse_cmd_with_args(self):
        """Parse ``foobar`` command with arguments"""
        cmd_name, cmd_args = parse_cmd(r'\foobar{foo}{bar}{baz}')
        self.assertEqual(cmd_name, 'foobar')
        self.assertEqual(cmd_args, ['foo', 'bar', 'baz'])

    def test_parse_cmd_without_args(self):
        """Parse ``foobar`` command without arguments"""
        cmd_name, cmd_args = parse_cmd(r'\foobar')
        self.assertEqual(cmd_name, 'foobar')
        self.assertEqual(cmd_args, [])

    def test_parse_cmd_colon(self):
        """Parse ``:`` command"""
        cmd_name, cmd_args = parse_cmd(r'\:')
        self.assertEqual(cmd_name, ':')
        self.assertEqual(cmd_args, [])

    def test_parse_cmd_fail(self):
        """It should fail on invalid command"""
        with self.assertRaises(ParseError):
            parse_cmd('not-a-valid-command')
