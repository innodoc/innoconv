# pylint: disable=missing-docstring,invalid-name

import unittest
import panflute as pf
from innoconv.constants import ELEMENT_CLASSES
from innoconv.mintmod_filter.filter_action import FilterAction, ParseError


class TestFilterAction(unittest.TestCase):
    def setUp(self):
        self.doc = pf.Doc()
        self.filter_action = FilterAction()

    def test_str_input(self):
        "filter() returns None if given Str element"
        elem_str = pf.Str('foo')
        ret = self._filter_elem([pf.Para(elem_str)], elem_str)
        self.assertIsNone(ret)  # None means element unchanged

    def test_math_input(self):
        "filter() returns Math if given Math element"
        elem_math = pf.Math(r'1+2')
        ret = self._filter_elem([pf.Para(elem_math)], elem_math)
        self.assertIsInstance(ret, pf.Math)

    def test_known_command(self):
        "filter() handles known LaTeX command"
        self.doc.content.extend([pf.RawBlock(r'\MTitle{Foo}', format='latex')])
        elem = self.doc.content[0]  # this sets up elem.parent
        ret = self._filter_elem([elem], elem)
        self.assertIsInstance(ret, pf.Header)

    def test_unknown_command_param(self):
        "filter() handles unknown LaTeX command"
        elem_unkown_cmd = pf.RawBlock(
            r'\ThisCommandAlsoDoesNotExist{foo}{bar}', format='latex')
        ret = self._filter_elem([elem_unkown_cmd], elem_unkown_cmd)
        self.assertIsInstance(ret, pf.Div)
        for cls in ELEMENT_CLASSES['UNKNOWN_CMD']:
            with self.subTest(cls=cls):
                self.assertIn(cls, ret.classes)
        self.assertIn('thiscommandalsodoesnotexist', ret.classes)

    def test_unknown_command(self):
        "filter() handles unknown LaTeX command"
        elem_unkown_cmd = pf.RawBlock(
            r'\ThisCommandDoesNotExist', format='latex')
        ret = self._filter_elem([elem_unkown_cmd], elem_unkown_cmd)
        self.assertIsInstance(ret, pf.Div)
        for cls in ELEMENT_CLASSES['UNKNOWN_CMD']:
            with self.subTest(cls=cls):
                self.assertIn(cls, ret.classes)
        self.assertIn('thiscommanddoesnotexist', ret.classes)

    def test_invalid_command(self):
        "filter() raises ParseError on invalid command"
        elem_invalid_cmd = pf.RawBlock(
            'This is not a valid LaTeX command', format='latex')
        with self.assertRaises(ParseError):
            self._filter_elem([elem_invalid_cmd], elem_invalid_cmd)

    def test_known_environment(self):
        "filter() handles known LaTeX environment"
        self.doc.content.extend([pf.RawBlock(
            r'\begin{MXContent}{FooShort}{Foo}{STD}'
            'FOOBARCONTENT'
            r'\end{MXContent}',
            format='latex')])
        elem_env = self.doc.content[0]  # this sets up elem.parent
        ret = self._filter_elem([elem_env], elem_env)
        self.assertIsInstance(ret, pf.Div)
        self.assertIsInstance(ret.content[0], pf.Header)
        self.assertIsInstance(ret.content[1], pf.Para)
        for cls in ELEMENT_CLASSES['MXCONTENT']:
            with self.subTest(cls=cls):
                self.assertIn(cls, ret.classes)

    def test_unknown_environment(self):
        "filter() handles unknown LaTeX environment"
        elem_env = pf.RawBlock(
            r'\begin{ThisEnvDoesNotExist}'
            'FOOBARCONTENT'
            r'\end{ThisEnvDoesNotExist}',
            format='latex')
        ret = self._filter_elem([elem_env], elem_env)
        self.assertIsInstance(ret, pf.Div)
        for cls in ELEMENT_CLASSES['UNKNOWN_ENV']:
            with self.subTest(cls=cls):
                self.assertIn(cls, ret.classes)
        self.assertIn('thisenvdoesnotexist', ret.classes)

    def test_invalid_environment(self):
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
        return self.filter_action.filter(test_elem, self.doc)
