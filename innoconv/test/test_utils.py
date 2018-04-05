"""This are unit tests for innoconv.utils"""

# pylint: disable=missing-docstring,invalid-name

import unittest
from mock import patch
import panflute as pf

from innoconv.errors import ParseError
from innoconv.utils import (parse_fragment, destringify, parse_cmd,
                            parse_nested_args, remove_empty_paragraphs,
                            remember_element, get_remembered_element)
from innoconv.test.utils import captured_output

CONTENT = r"""
\documentclass[12pt]{article}
\begin{document}

\section{Test heading}

Lorem ipsum dolor sit amet, consectetur adipiscing elit. In luctus
eget lorem ut tincidunt. Duis nunc quam, vehicula et molestie
consectetur, maximus nec sapien. In posuere venenatis fringilla. Sed
ac mi vehicula, blandit elit id, rutrum tellus. Praesent consectetur
lacinia quam, nec molestie neque ultricies eget. Donec eget facilisis
nisi. Suspendisse condimentum facilisis molestie. Donec vehicula dui
vel ligula laoreet porta.

\subsection{Another heading}

Aliquam sit amet lorem nec mauris venenatis volutpat quis et
mauris. Aenean nec ullamcorper orci, at euismod ipsum. Sed ac risus
tortor. Class aptent taciti sociosqu ad litora torquent per conubia
nostra, per inceptos himenaeos. Nullam tincidunt euismod felis, in
varius quam. Mauris lobortis elit mollis nisi imperdiet, at sagittis
libero elementum. Donec hendrerit ex libero, ut condimentum ligula
porttitor at. Pellentesque libero urna, egestas a semper in, auctor
vitae tellus. In quis viverra nibh.

\end{document}
"""


class TestParseFragment(unittest.TestCase):

    def test_parse_fragment(self):
        """parse_fragment() returns valid output if given test document"""
        doc = parse_fragment(CONTENT)
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
        """if given broken document parse_fragment() raises RuntimeError and
        prints errors"""
        with captured_output() as out:
            with self.assertRaises(RuntimeError):
                parse_fragment(r'\begin{fooenv}bla')
            err_out = out[1].getvalue()
        self.assertTrue('ERROR' in err_out)

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

    def test_parse_cmd_nested(self):
        """It should parse nested commands"""
        cmd_name, cmd_args = parse_cmd(r'\foobar{word\bar{two}bbb}{baz}')
        self.assertEqual(cmd_name, 'foobar')
        self.assertEqual(cmd_args, [r'word\bar{two}bbb', 'baz'])


class TestParseNestedArgs(unittest.TestCase):

    def test_parse_nested_args_empty(self):
        """It should parse nested arguments: empty"""
        cmd_args = list(parse_nested_args(''))
        self.assertEqual(cmd_args, [])

    def test_parse_nested_args_simple(self):
        """It should parse nested arguments: simple"""
        cmd_args = list(parse_nested_args('{bbb}{baz}{foo}'))
        self.assertEqual(cmd_args, ['bbb', 'baz', 'foo'])

    def test_parse_nested_args_1(self):
        """It should parse nested arguments: nested 1"""
        cmd_args = list(parse_nested_args(r'{word\bar{two}bbb}{baz}'))
        self.assertEqual(cmd_args, [r'word\bar{two}bbb', 'baz'])

    def test_parse_nested_args_2(self):
        """It should parse nested arguments: nested 2"""
        cmd_args = list(parse_nested_args(
            r'{cont}{}{\foo{\bla{\stop}}}{\baz{}{}{}}'))
        self.assertEqual(cmd_args,
                         ['cont', '', r'\foo{\bla{\stop}}', r'\baz{}{}{}'])


class TestRemoveEmptyParagraphs(unittest.TestCase):

    def test_remove_empty_paragraphs(self):
        """It should remove empty paras in document"""
        doc = pf.Doc(
            pf.Para(pf.Str('Foo'), pf.Space(), pf.Str('Bar')),
            pf.Para(),
            pf.Para(pf.Str('Bar'), pf.Space(), pf.Str('Baz')),
        )
        remove_empty_paragraphs(doc)
        self.assertEqual(len(doc.content), 2)
        para1 = doc.content[0]
        self.assertEqual(para1.content[0].text, 'Foo')
        self.assertEqual(para1.content[2].text, 'Bar')
        para2 = doc.content[1]
        self.assertEqual(para2.content[0].text, 'Bar')
        self.assertEqual(para2.content[2].text, 'Baz')


class TestRememberElement(unittest.TestCase):

    def test_remember_element(self):
        """It should remember and forget elements."""
        doc = pf.Doc()

        self.assertIsNone(get_remembered_element(doc))

        header = pf.Header()
        remember_element(doc, header)
        rememembered_el = get_remembered_element(doc)
        self.assertEqual(rememembered_el, header)
        self.assertIsNone(get_remembered_element(doc))

        img = pf.Image()
        remember_element(doc, img)
        rememembered_img = get_remembered_element(doc)
        self.assertEqual(rememembered_img, img)
        self.assertIsNone(get_remembered_element(doc))
