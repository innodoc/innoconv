import unittest
import panflute as pf
from mintmod_filter.filter_action import FilterAction, CLASS_UNKNOWN_CMD


class TestFilterAction(unittest.TestCase):
    def setUp(self):
        self.fa = FilterAction()
        self.elem_str = pf.Str('foo')
        self.elem_math = pf.Math(r'1+2')
        self.elem_mtitle = pf.RawBlock('\MTitle{Foo}', format='latex')
        self.elem_unkown_cmd = pf.RawBlock(
            '\ThisCommandDoesNotExist{Foo}', format='latex')
        self.elem_unkown_raw_block = pf.RawBlock(
            'NotAValidLatexCommand', format='latex')
        block = pf.Block(
            self.elem_str,
            self.elem_math,
            self.elem_mtitle,
            self.elem_unkown_cmd,
            self.elem_unkown_raw_block,
        )
        self.doc = pf.Doc(block)

    def test_str_input(self):
        "filter() returns None if given Str element"
        ret = self.fa.filter(self.elem_str, self.doc)
        self.assertIsNone(ret)

    def test_math_input(self):
        "filter() returns Math if given Math element"
        ret = self.fa.filter(self.elem_math, self.doc)
        self.assertEqual(type(ret), pf.Math)

    def test_known_latex_rawblock_command(self):
        "filter() handles known LaTeX command"
        ret = self.fa.filter(self.elem_mtitle, self.doc)
        self.assertEqual(type(ret), pf.Header)

    def test_unknown_latex_rawblock_input(self):
        "filter() handles unknown LaTeX command"
        div = self.fa.filter(self.elem_unkown_cmd, self.doc)
        self.assertEqual(type(div), pf.Div)
        self.assertIn(CLASS_UNKNOWN_CMD, div.classes)
        self.assertIn('thiscommanddoesnotexist', div.classes)

    def test_unhandled_rawblock_input(self):
        "filter() handles unknown RawBlock"
        ret = self.fa.filter(self.elem_unkown_raw_block, self.doc)
        self.assertIsNone(ret)
