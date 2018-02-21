import unittest
import panflute as pf
from mintmod_filter.constants import CSS_CLASSES
from mintmod_filter.filter_action import FilterAction, ParseError


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

    def test_unknown_latex_rawblock_command_with_param(self):
        "filter() handles unknown LaTeX command"
        elem_unkown_cmd = pf.RawBlock(
            r'\ThisCommandAlsoDoesNotExist{foo}{bar}', format='latex')
        ret = self._filter_elem([elem_unkown_cmd], elem_unkown_cmd)
        self.assertEqual(type(ret), pf.Div)
        for cls in CSS_CLASSES['UNKNOWN_CMD']:
            self.assertIn(cls, ret.classes)
        self.assertIn('thiscommandalsodoesnotexist', ret.classes)

    def test_unknown_latex_rawblock_command(self):
        "filter() handles unknown LaTeX command"
        elem_unkown_cmd = pf.RawBlock(
            r'\ThisCommandDoesNotExist', format='latex')
        ret = self._filter_elem([elem_unkown_cmd], elem_unkown_cmd)
        self.assertEqual(type(ret), pf.Div)
        for cls in CSS_CLASSES['UNKNOWN_CMD']:
            self.assertIn(cls, ret.classes)
        self.assertIn('thiscommanddoesnotexist', ret.classes)

    def test_invalid_latex_rawblock_command(self):
        "filter() raises ParseError on invalid command"
        elem_invalid_cmd = pf.RawBlock(
            'This is not a valid LaTeX command', format='latex')
        with self.assertRaises(ParseError):
            self._filter_elem([elem_invalid_cmd], elem_invalid_cmd)

    def test_known_latex_rawblock_environment(self):
        "filter() handles known LaTeX environment"
        elem_env = pf.RawBlock(
            r'\begin{MXContent}{FooShort}{Foo}{STD}'
            'FOOBARCONTENT'
            r'\end{MXContent}',
            format='latex')
        ret = self._filter_elem([elem_env], elem_env)
        self.assertEqual(type(ret), pf.Div)
        self.assertEqual(type(ret.content[0]), pf.Header)
        self.assertEqual(type(ret.content[1]), pf.Para)
        for cls in CSS_CLASSES['MXCONTENT']:
            self.assertIn(cls, ret.classes)

    def test_unknown_latex_rawblock_environment(self):
        "filter() handles unknown LaTeX environment"
        elem_env = pf.RawBlock(
            r'\begin{ThisEnvDoesNotExist}'
            'FOOBARCONTENT'
            r'\end{ThisEnvDoesNotExist}',
            format='latex')
        ret = self._filter_elem([elem_env], elem_env)
        self.assertEqual(type(ret), pf.Div)
        for cls in CSS_CLASSES['UNKNOWN_ENV']:
            self.assertIn(cls, ret.classes)
        self.assertIn('thisenvdoesnotexist', ret.classes)

    def test_invalid_latex_rawblock_environment(self):
        "filter() raises ParseError on invalid environment"
        elem_invalid_env = pf.RawBlock(
            r'/begin'
            'FOOBARCONTENT'
            r'\end{ThisEnvDoesNotExist}',
            format='latex')
        with self.assertRaises(ParseError):
            self._filter_elem([elem_invalid_env], elem_invalid_env)

    def _filter_elem(self, elem_list, test_elem):
        self.doc.content.extend(elem_list)
        return self.fa.filter(test_elem, self.doc)
