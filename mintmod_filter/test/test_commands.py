# pylint: disable=missing-docstring,invalid-name

import unittest
import panflute as pf
from mintmod_filter.commands import Commands


class TestCommands(unittest.TestCase):

    def setUp(self):
        self.commands = Commands()

    def test_handle_msection(self):
        doc = pf.Doc(pf.RawBlock(r'\MSection{A Test Title}'), format='latex')
        elem = doc.content[0]  # this sets up elem.parent
        ret = self.commands.handle_msection(["A Test Title"], elem)

        self.assertEqual(ret, [])

        last_header_elem = getattr(doc, "last_header_elem")

        self.assertIsInstance(last_header_elem, pf.Header)
        self.assertIsInstance(last_header_elem.content[0], pf.Str)
        self.assertEqual(last_header_elem.content[0].text, 'A')
        self.assertIsInstance(last_header_elem.content[1], pf.Space)
        self.assertIsInstance(last_header_elem.content[2], pf.Str)
        self.assertEqual(last_header_elem.content[2].text, 'Test')
        self.assertIsInstance(last_header_elem.content[4], pf.Str)
        self.assertEqual(last_header_elem.content[4].text, 'Title')
        self.assertEqual(last_header_elem.identifier, "a-test-title")
        self.assertEqual(last_header_elem.level, 2)

    def test_handle_msref(self):
        doc = pf.Doc(pf.RawBlock(r'\MSRef{fooid}{linktext}'), format='latex')
        elem = doc.content[0]  # this sets up elem.parent
        ret = self.commands.handle_msref(['fooid', 'linktext'], elem)
        self.assertIsInstance(ret, pf.Link)
        self.assertIsInstance(ret.content[0], pf.Str)
        self.assertEqual(ret.content[0].text, 'linktext')
        self.assertEqual(ret.url, '#fooid')

    def test_handle_mextlink(self):
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
        doc = pf.Doc(pf.RawBlock(r'\MSubject{footitle}', format='latex'))
        elem = doc.content[0]  # this sets up elem.parent
        ret = self.commands.handle_msubject(['footitle'], elem)
        self.assertEqual(ret, [])
        self.assertIsInstance(doc.metadata, pf.MetaMap)
        # pylint: disable=no-member
        self.assertEqual(doc.get_metadata('title'), 'footitle')

    def test_handle_mugraphics_block(self):
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
        content = r'\MUGraphics{foobar.png}{width=0.3\linewidth}{Footitle}'
        doc = pf.Doc(pf.Para(pf.RawInline(content, format='latex')))
        elem = doc.content[0].content[0]  # this sets up elem.parent
        elem_args = ['foobar.png', r'width=0.3\linewidth', 'Footitle']
        ret = self.commands.handle_mugraphics(elem_args, elem)
        self.assertIsInstance(ret, pf.Image)
        self.assertEqual(ret.url, 'foobar.png')
        self.assertEqual(ret.title, 'Footitle')

    def test_handle_mugraphicssolo_block(self):
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
        content = r'\MUGraphicsSolo{foo.jpg}{width=0.3\linewidth}{}'
        doc = pf.Doc(pf.Para(pf.RawInline(content, format='latex')))
        elem = doc.content[0].content[0]  # this sets up elem.parent
        elem_args = ['foo.jpg', r'width=0.3\linewidth', '']
        ret = self.commands.handle_mugraphicssolo(elem_args, elem)
        self.assertIsInstance(ret, pf.Image)
        self.assertEqual(ret.url, 'foo.jpg')

    def test_handle_glqq(self):
        elem = pf.RawInline(r'\glqq', format='latex')
        elem_repl = self.commands.handle_glqq([], elem)
        self.assertEqual(elem_repl.text, r'„')

    def test_handle_grqq(self):
        elem = pf.RawInline(r'\grqq', format='latex')
        elem_repl = self.commands.handle_grqq([], elem)
        self.assertEqual(elem_repl.text, r'“')
