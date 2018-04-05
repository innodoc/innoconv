# pylint: disable=missing-docstring, invalid-name, too-many-public-methods

import unittest
import panflute as pf

from innoconv import utils
from innoconv.constants import INDEX_LABEL_PREFIX
from innoconv.mintmod_filter.commands import Commands


class TestCommands(unittest.TestCase):

    def setUp(self):
        self.commands = Commands()

    def test_handle_msection(self):
        """MSection command"""
        doc = pf.Doc(pf.RawBlock(r'\MSection{A Test Title}'), format='latex')
        elem = doc.content[0]  # this sets up elem.parent
        ret = self.commands.handle_msection(['A Test Title'], elem)

        self.assertEqual(ret, [])

        last_header_elem = getattr(doc, 'last_header_elem')

        self.assertIsInstance(last_header_elem, pf.Header)
        self.assertIsInstance(last_header_elem.content[0], pf.Str)
        self.assertEqual(last_header_elem.content[0].text, 'A')
        self.assertIsInstance(last_header_elem.content[1], pf.Space)
        self.assertIsInstance(last_header_elem.content[2], pf.Str)
        self.assertEqual(last_header_elem.content[2].text, 'Test')
        self.assertIsInstance(last_header_elem.content[4], pf.Str)
        self.assertEqual(last_header_elem.content[4].text, 'Title')
        self.assertEqual(last_header_elem.level, 2)

    def test_handle_msubsection(self):
        """MSubsection command"""
        doc = pf.Doc(pf.RawBlock(r'\MSubsection{Foo title}'), format='latex')
        elem = doc.content[0]
        ret = self.commands.handle_msubsection(['Foo title'], elem)
        self.assertIsInstance(ret, pf.Header)
        self.assertIsInstance(ret.content[0], pf.Str)
        self.assertEqual(ret.content[0].text, 'Foo')
        self.assertIsInstance(ret.content[1], pf.Space)
        self.assertIsInstance(ret.content[2], pf.Str)
        self.assertEqual(ret.content[2].text, 'title')
        self.assertEqual(ret.level, 3)

    def test_handle_mtitle(self):
        """MTitle command"""
        doc = pf.Doc(
            pf.RawBlock(r'\MTitle{Schöne Titel nach Maß?}'), format='latex')
        elem = doc.content[0]
        ret = self.commands.handle_mtitle([u'Schöne Titel nach Maß?'], elem)
        self.assertIsInstance(ret, pf.Header)
        self.assertIsInstance(ret.content[0], pf.Str)
        self.assertEqual(ret.content[0].text, u'Schöne')
        self.assertIsInstance(ret.content[6], pf.Str)
        self.assertEqual(ret.content[6].text, u'Maß?')
        self.assertEqual(ret.level, 4)

    def test_handle_mlabel_no_last_header(self):
        """MTitle command without a last header element"""
        doc = pf.Doc(pf.RawBlock(r'\MLabel{TEST_LABEL}'), format='latex')
        elem = doc.content[0]
        ret = self.commands.handle_mlabel(['TEST_LABEL'], elem)
        self.assertIsInstance(ret, pf.Div)
        self.assertIn(INDEX_LABEL_PREFIX, ret.classes)
        self.assertEqual(
            ret.identifier, '{}-TEST_LABEL'.format(INDEX_LABEL_PREFIX))

    def test_handle_mlabel_last_header(self):
        """MTitle command with a last header element"""
        mlabel = pf.RawBlock(r'\MLabel{TEST_LABEL}')
        header = pf.Header(pf.Str('headertext'))
        doc = pf.Doc(header, mlabel, format='latex')
        doc.last_header_elem = header
        elem = doc.content[0]
        ret = self.commands.handle_mlabel(['HEADER'], elem)
        self.assertFalse(ret)
        # pylint: disable=no-member
        self.assertEqual(header.identifier, 'HEADER')

    def test_handle_special_html(self):
        """special command embedded html"""
        doc = pf.Doc(
            pf.RawBlock(
                r'\special{html:<a href="http://www.example.com">Bar</a>}'),
            format='latex')
        elem = doc.content[0]
        ret = self.commands.handle_special(
            [r'html:<a href="http://www.example.com">Bar</a>'], elem)
        self.assertIsInstance(ret, pf.RawBlock)
        self.assertEqual(ret.format, 'html')
        self.assertEqual(
            ret.text, '<a href="http://www.example.com">Bar</a>')

    def test_handle_special_html_replacing(self):
        """special command should not remove 'html:' in the middle of a
        string."""
        doc = pf.Doc(
            pf.RawBlock(
                r'\special{html:<a href="#bar">html:</a>}'),
            format='latex')
        elem = doc.content[0]
        ret = self.commands.handle_special(
            [r'html:<a href="#bar">html:</a>'], elem)
        self.assertIsInstance(ret, pf.RawBlock)
        self.assertEqual(ret.format, 'html')
        self.assertEqual(
            ret.text, '<a href="#bar">html:</a>')

    def test_handle_special_detect_html(self):
        """special command should not be confused by a 'html:'."""
        doc = pf.Doc(
            pf.RawBlock(
                r'\special{bar:<a href="#foo">html:</a>}'),
            format='latex')
        elem = doc.content[0]
        ret = self.commands.handle_special(
            [r'bar:<a href="#foo">html:</a>'], elem)
        self.assertIsNone(ret)

    def test_handle_special_other(self):
        """special command with non-html code should be ignored"""
        # Note: 'html:' occuring in the middle of the string.
        doc = pf.Doc(
            pf.RawBlock(
                r'\special{python:print("html:")}'),
            format='latex')
        elem = doc.content[0]
        ret = self.commands.handle_special(
            [r'python:print("html:")'], elem)
        self.assertIsNone(ret)

    def test_handle_mssectionlabelprefix(self):
        # TODO implement handle_mssectionlabelprefix, not specified, see #4
        pass

    def test_handle_msref(self):
        """MSRef command"""
        doc = pf.Doc(pf.RawBlock(r'\MSRef{fooid}{linktext}'), format='latex')
        elem = doc.content[0]  # this sets up elem.parent
        ret = self.commands.handle_msref(['fooid', 'linktext'], elem)
        self.assertIsInstance(ret, pf.Link)
        self.assertIsInstance(ret.content[0], pf.Str)
        self.assertEqual(ret.content[0].text, 'linktext')
        self.assertEqual(ret.url, '#fooid')

    def test_handle_mextlink(self):
        """MExtLink command"""
        block = pf.Para(
            pf.RawInline(
                r'\MExtLink{https://www.example.com/}{Example link}',
                format='latex'
            )
        )
        doc = pf.Doc(block)
        elem = doc.content[0].content[0]  # this sets up elem.parent
        ret = self.commands.handle_mextlink(
            ['https://www.example.com/', 'Example link'], elem)
        self.assertIsInstance(ret, pf.Link)
        self.assertIsInstance(ret.content[0], pf.Str)
        self.assertEqual(ret.content[0].text, 'Example')
        self.assertEqual(ret.url, 'https://www.example.com/')

    def test_handle_msubject(self):
        """MSubject command"""
        doc = pf.Doc(pf.RawBlock(r'\MSubject{footitle}', format='latex'))
        elem = doc.content[0]  # this sets up elem.parent
        ret = self.commands.handle_msubject(['footitle'], elem)
        self.assertEqual(ret, [])
        self.assertIsInstance(doc.metadata, pf.MetaMap)
        # pylint: disable=no-member
        self.assertEqual(doc.get_metadata('title'), 'footitle')

    def test_handle_mugraphics_block(self):
        """MUGraphics command (block)"""
        content = r'\MUGraphics{foobar.png}{width=0.3\linewidth}{Footitle}'
        doc = pf.Doc(pf.RawBlock(content, format='latex'))
        elem = doc.content[0]  # this sets up elem.parent
        elem_args = ['foobar.png', r'width=0.3\linewidth', 'Footitle']
        ret = self.commands.handle_mugraphics(elem_args, elem)
        self.assertIsInstance(ret, pf.Div)
        img = ret.content[0].content[0]
        self.assertIsInstance(img, pf.Image)
        self.assertEqual(img.url, 'foobar.png')
        self.assertEqual(img.title, 'Footitle')

    def test_handle_mugraphics_inline(self):
        """MUGraphics command (inline)"""
        content = r'\MUGraphics{foobar.png}{width=0.3\linewidth}{Footitle}'
        doc = pf.Doc(pf.Para(pf.RawInline(content, format='latex')))
        elem = doc.content[0].content[0]  # this sets up elem.parent
        elem_args = ['foobar.png', r'width=0.3\linewidth', 'Footitle']
        ret = self.commands.handle_mugraphics(elem_args, elem)
        self.assertIsInstance(ret, pf.Image)
        self.assertEqual(ret.url, 'foobar.png')
        self.assertEqual(ret.title, 'Footitle')

    def test_handle_mugraphicssolo_block(self):
        """MUGraphicsSolo command (block)"""
        content = r'\MUGraphicsSolo{foobar.png}{width=0.3\linewidth}{}'
        doc = pf.Doc(pf.RawBlock(content, format='latex'))
        elem = doc.content[0]  # this sets up elem.parent
        elem_args = ['foobar.png', r'width=0.3\linewidth', '']
        ret = self.commands.handle_mugraphicssolo(elem_args, elem)
        self.assertIsInstance(ret, pf.Div)
        img = ret.content[0].content[0]
        self.assertIsInstance(img, pf.Image)
        self.assertEqual(img.url, 'foobar.png')

    def test_handle_mugraphicssolo_inline(self):
        """MUGraphicsSolo command (inline)"""
        content = r'\MUGraphicsSolo{foo.jpg}{width=0.3\linewidth}{}'
        doc = pf.Doc(pf.Para(pf.RawInline(content, format='latex')))
        elem = doc.content[0].content[0]  # this sets up elem.parent
        elem_args = ['foo.jpg', r'width=0.3\linewidth', '']
        ret = self.commands.handle_mugraphicssolo(elem_args, elem)
        self.assertIsInstance(ret, pf.Image)
        self.assertEqual(ret.url, 'foo.jpg')

    def test_handle_glqq(self):
        """glqq"""
        elem = pf.RawInline(r'\glqq', format='latex')
        elem_repl = self.commands.handle_glqq([], elem)
        self.assertEqual(elem_repl.text, r'„')

    def test_handle_grqq(self):
        """grqq"""
        elem = pf.RawInline(r'\grqq', format='latex')
        elem_repl = self.commands.handle_grqq([], elem)
        self.assertEqual(elem_repl.text, r'“')

    def test_handle_myoutubevideo(self):
        command = r'''\MYoutubeVideo{Newtons Laws (2)}{400}{300}{https://www.you
        tube.com/embed/WzvhuQ5RWJE?rel=0&amp;wmode=transparent}'''
        elem, args = utils.parse_cmd(command)
        ret = self.commands.handle_myoutubevideo(args, elem)
        self.assertIsInstance(ret, pf.Link)
        # pylint: disable=no-member
        self.assertEqual(ret.attributes['width'], '400')
        self.assertEqual(ret.attributes['height'], '300')
        self.assertEqual(ret.title, args[0])

    def test_noops(self):
        """Test no-op commands."""
        noops = (
            (
                self.commands.handle_mdeclaresiteuxid,
                ['FOO'], r'\MDeclareSiteUXID{FOO}',
            ),
            (
                self.commands.handle_mmodstartbox,
                [], r'\MModstartBox',
            ),
            (
                self.commands.handle_mpragma,
                ['MathSkip'], r'\MPragma{MathSkip}',
            ),
        )
        for handler, elem_args, elem_code in noops:
            with self.subTest(name=handler.__name__):
                ret = handler(elem_args, pf.RawBlock(elem_code))
                self.assertListEqual(ret, [])
