# pylint: disable=missing-docstring, invalid-name, too-many-public-methods

import unittest
import panflute as pf

from innoconv.constants import (ELEMENT_CLASSES, INDEX_LABEL_PREFIX,
                                QUESTION_TYPES)
from innoconv.mintmod_filter.commands import Commands
from innoconv.utils import remember_element


class TestCommands(unittest.TestCase):

    def setUp(self):
        self.commands = Commands()

    def test_handle_msection(self):
        """MSection command"""
        doc = pf.Doc(pf.RawBlock(r'\MSection{A Test Title}'), format='latex')
        elem = doc.content[0]  # this sets up elem.parent
        ret = self.commands.handle_msection(['A Test Title'], elem)

        self.assertIsInstance(ret, pf.Header)
        self.assertEqual(ret.level, 1)
        self.assertIsInstance(ret.content[0], pf.Str)
        self.assertEqual(ret.content[0].text, 'A')
        self.assertIsInstance(ret.content[1], pf.Space)
        self.assertIsInstance(ret.content[2], pf.Str)
        self.assertEqual(ret.content[2].text, 'Test')
        self.assertIsInstance(ret.content[4], pf.Str)
        self.assertEqual(ret.content[4].text, 'Title')

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
        self.assertEqual(ret.level, 2)

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

    def test_handle_msubsubsubsectionx(self):
        doc = pf.Doc(pf.RawBlock(r'\MSubsubsubsectionx{Subsubsubsectionx}'),
                     format='latex')
        elem = doc.content[0]
        ret = self.commands.handle_msubsubsubsectionx(
            ['Subsubsubsectionx'], elem)
        self.assertIsInstance(ret, pf.Header)
        self.assertIsInstance(ret.content[0], pf.Str)
        self.assertEqual(ret.content[0].text, u'Subsubsubsectionx')
        self.assertEqual(ret.level, 5)

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
        mlabel = pf.RawBlock(r'\MLabel{HEADER}')
        header = pf.Header(pf.Str('headertext'))
        doc = pf.Doc(header, mlabel, format='latex')
        elem = doc.content[0]
        remember_element(doc, elem)
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

    def test_handle_msref(self):
        """MSRef command"""
        doc = pf.Doc(pf.RawBlock(r'\MSRef{fooid}{linktext}'), format='latex')
        elem = doc.content[0]  # this sets up elem.parent
        ret = self.commands.handle_msref(['fooid', 'linktext'], elem)
        link = ret.content[0]
        self.assertIsInstance(link, pf.Link)
        self.assertIsInstance(link.content[0], pf.Str)
        self.assertEqual(link.content[0].text, 'linktext')
        self.assertEqual(link.url, '#fooid')

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
        self.assertIsInstance(ret, pf.Header)
        self.assertEqual(ret.level, 1)
        self.assertEqual(ret.content[0].text, 'footitle')
        self.assertIsInstance(doc.metadata, pf.MetaMap)
        # pylint: disable=no-member
        self.assertEqual(doc.get_metadata('title'), 'footitle')

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
        video = pf.RawBlock(
            r'\MYoutubeVideo{Newtons Laws (2)}{400}{300}'
            '{https://www.youtube.com/embed/WzvhuQ5RWJE}',
            format='latex'
        )
        doc = pf.Doc(video)
        elem = doc.content[0]  # this sets up elem.parent
        cmd_args = ['Newtons Laws (2)', '400', '300',
                    'https://www.youtube.com/embed/WzvhuQ5RWJE']
        ret = self.commands.handle_myoutubevideo(cmd_args, elem)
        self.assertIsInstance(ret.content[0], pf.Link)
        self.assertEqual(ret.content[0].title, 'Newtons Laws (2)')

    def test_handle_mvideo(self):
        video = pf.RawBlock(
            r'\MVideo{vidbsp1}{Carry out a case analysis.}',
            format='latex'
        )
        doc = pf.Doc(video)
        elem = doc.content[0]  # this sets up elem.parent
        cmd_args = ['vidbsp1', 'Carry out a case analysis.']
        ret = self.commands.handle_mvideo(cmd_args, elem)
        self.assertIsInstance(ret.content[0], pf.Link)
        self.assertEqual(ret.content[0].title, 'Carry out a case analysis.')
        self.assertEqual(ret.content[0].url, 'vidbsp1.mp4')

    def test_handle_mzahl(self):
        r"""Test \MZahl outside of Math environment"""
        elem = pf.RawInline(r'\MZahl{1}{2}', format='latex')
        ret = self.commands.handle_mzahl(['1', '2'], elem)
        self.assertIsInstance(ret, pf.Math)
        self.assertEqual(ret.text, r'\num{1.2}')

    def test_handle_mentry(self):
        r"""\MEntry without math"""
        elem = pf.RawInline(r'\MEntry{Bla bla}{bla}', format='latex')
        ret = self.commands.handle_mentry(['Bla bla', 'bla'], elem)
        self.assertIsInstance(ret, pf.Span)
        self.assertEqual('index-bla', ret.identifier)
        strong = ret.content[0]
        self.assertIsInstance(strong, pf.Strong)
        self.assertEqual(strong.content[0].text, 'Bla')
        self.assertEqual(strong.content[2].text, 'bla')

    def test_handle_mentry_math(self):
        r"""\MEntry with math inside"""
        elem = pf.RawInline(
            r'\MEntry{$\MTextSF{floor}$-Funktion}{floor-Funktion}',
            format='latex')
        ret = self.commands.handle_mentry([
            r'$\MTextSF{floor}$-Funktion', 'floor-Funktion'], elem)
        self.assertIsInstance(ret, pf.Span)
        self.assertEqual('index-floor-funktion', ret.identifier)
        strong = ret.content[0]
        self.assertIsInstance(strong, pf.Strong)
        self.assertIsInstance(strong.content[0], pf.Math)
        self.assertEqual(strong.content[0].text, r'\textsf{floor}')
        self.assertEqual(strong.content[1].text, '-Funktion')

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


class TestFormatting(unittest.TestCase):

    def setUp(self):
        self.commands = Commands()

    def test_handle_modstextbf(self):
        """modstextbf command"""
        content = r'\modstextbf{foo $x^2$}'
        doc = pf.Doc(pf.RawBlock(content, format='latex'))
        elem = doc.content[0]  # this sets up elem.parent
        strong = self.commands.handle_modstextbf(['foo $x^2$'], elem)
        self.assertIsInstance(strong, pf.Strong)
        string = strong.content[0]
        self.assertIsInstance(string, pf.Str)
        self.assertEqual(string.text, 'foo')
        self.assertIsInstance(strong.content[1], pf.Space)
        math = strong.content[2]
        self.assertIsInstance(math, pf.Math)
        self.assertEqual(math.text, 'x^2')

    def test_handle_modsemph(self):
        """modsemph command"""
        content = r'\modsemph{foo $x^2$}'
        doc = pf.Doc(pf.RawBlock(content, format='latex'))
        elem = doc.content[0]  # this sets up elem.parent
        emph = self.commands.handle_modsemph(['foo $x^2$'], elem)
        self.assertIsInstance(emph, pf.Emph)
        string = emph.content[0]
        self.assertIsInstance(string, pf.Str)
        self.assertEqual(string.text, 'foo')
        self.assertIsInstance(emph.content[1], pf.Space)
        math = emph.content[2]
        self.assertIsInstance(math, pf.Math)
        self.assertEqual(math.text, 'x^2')

    def test_handle_highlight(self):
        """highlight command"""
        content = r'\highlight{foo $x^2$}'
        doc = pf.Doc(pf.RawBlock(content, format='latex'))
        elem = doc.content[0]  # this sets up elem.parent
        highlight = self.commands.handle_highlight(['foo $x^2$'], elem)
        self.assertIsInstance(highlight, pf.Span)
        for cls in ELEMENT_CLASSES['HIGHLIGHT']:
            self.assertIn(cls, getattr(highlight, 'classes'))
        string = highlight.content[0]
        self.assertIsInstance(string, pf.Str)
        self.assertEqual(string.text, 'foo')
        self.assertIsInstance(highlight.content[1], pf.Space)
        math = highlight.content[2]
        self.assertIsInstance(math, pf.Math)
        self.assertEqual(math.text, 'x^2')

    def test_handle_newline(self):
        """newline command"""
        content = r'\newline'
        doc = pf.Doc(pf.RawBlock(content, format='latex'))
        elem = doc.content[0]  # this sets up elem.parent
        ret = self.commands.handle_newline([], elem)
        self.assertIsInstance(ret, pf.LineBreak)


class TestGraphics(unittest.TestCase):

    def setUp(self):
        self.commands = Commands()

    def test_handle_mugraphics_block(self):
        """MUGraphics command (block) with description"""
        content = r'\MUGraphics{foobar.png}{width=0.3\linewidth}' \
            '{Footitle $a^2$}'
        doc = pf.Doc(pf.RawBlock(content, format='latex'))
        elem = doc.content[0]  # this sets up elem.parent
        elem_args = ['foobar.png', r'width=0.3\linewidth', 'Footitle $a^2$']
        ret = self.commands.handle_mugraphics(elem_args, elem)
        self.assertIsInstance(ret, pf.Div)

        img = ret.content[0].content[0]
        self.assertIsInstance(img, pf.Image)
        self.assertEqual(img.url, 'foobar.png')
        self.assertEqual(img.title, 'Footitle a^2')

        descr = ret.content[1]
        self.assertIsInstance(descr, pf.Para)

        descr1 = descr.content[0]
        self.assertIsInstance(descr1, pf.Str)
        self.assertEqual(descr1.text, 'Footitle')
        descr2 = descr.content[1]
        self.assertIsInstance(descr2, pf.Space)
        descr3 = descr.content[2]
        self.assertIsInstance(descr3, pf.Math)

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


class TestExercises(unittest.TestCase):

    def setUp(self):
        self.commands = Commands()

    def test_handle_mquestion(self):
        """MQuestion command inline"""
        content = r'\MLParsedQuestion{10}{5}{3}{ER1}'
        doc = pf.Doc(pf.RawBlock(content), format='latex')
        elem = doc.content[0]  # this sets up elem.parent
        elem_args = ['10', '5', '3', 'ER1']
        ret = self.commands.handle_mlparsedquestion(elem_args, elem)
        # pylint: disable=no-member
        self.assertEqual(ret.classes, ['exercise', 'text'])
        self.assertEqual(ret.attributes['length'], '10')
        self.assertEqual(ret.attributes['solution'], '5')
        self.assertEqual(ret.attributes['precision'], '3')
        self.assertEqual(ret.attributes['uxid'], 'ER1')
        self.assertEqual(
            ret.attributes['questionType'], QUESTION_TYPES['MATH_EXPRESSION']
        )
