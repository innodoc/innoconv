import unittest
import panflute as pf
from mintmod_filter.filter_action import FilterAction, CLASS_UNKNOWN_CMD


class TestFilterAction(unittest.TestCase):
    def setUp(self):
        self.fa = FilterAction()
        self.doc = pf.Doc()

    def test_str_input(self):
        "filter() returns None if given Str element"
        elem_str = pf.Str('foo')
        ret = self._filter_elem([pf.Para(elem_str)], elem_str)
        self.assertIsNone(ret)

    def test_math_input(self):
        "filter() returns Math if given Math element"
        elem_math = pf.Math(r'1+2')
        ret = self._filter_elem([pf.Para(elem_math)], elem_math)
        self.assertEqual(type(ret), pf.Math)

    def test_known_latex_rawblock_command(self):
        "filter() handles known LaTeX command"
        elem_mtitle = pf.RawBlock('\MTitle{Foo}', format='latex')
        ret = self._filter_elem([elem_mtitle], elem_mtitle)
        self.assertEqual(type(ret), pf.Header)

    def test_unknown_latex_rawblock_input(self):
        "filter() handles unknown LaTeX command"
        elem_unkown_cmd = pf.RawBlock(
            '\ThisCommandDoesNotExist{Foo}', format='latex')
        ret = self._filter_elem([elem_unkown_cmd], elem_unkown_cmd)
        self.assertEqual(type(ret), pf.Div)
        self.assertIn(CLASS_UNKNOWN_CMD, ret.classes)
        self.assertIn('thiscommanddoesnotexist', ret.classes)

    def test_unhandled_rawblock_input(self):
        "filter() handles unknown RawBlock"
        elem_unkown_raw_block = pf.RawBlock(
            'NotAValidLatexCommand', format='latex')
        ret = self._filter_elem([elem_unkown_raw_block], elem_unkown_raw_block)
        self.assertIsNone(ret)

    def _filter_elem(self, elem_list, test_elem):
        self.doc.content.extend(elem_list)
        return self.fa.filter(test_elem, self.doc)
