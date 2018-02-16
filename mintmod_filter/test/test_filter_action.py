import unittest
import panflute as pf
from mintmod_filter.filter_action import FilterAction


class TestFilterAction(unittest.TestCase):
    @classmethod
    def setUp(self):
        self.fa = FilterAction()
        self.elem_str = pf.Str('foo')
        self.elem_math = pf.Math(r'1+2')
        self.doc = pf.Doc(pf.Block(self.elem_str, self.elem_math))

    def test_str_input(self):
        "filter() returns None if given Str element"
        ret = self.fa.filter(self.elem_str, self.doc)
        self.assertIsNone(ret)

    def test_math_input(self):
        "filter() returns Math if given Math element"
        ret = self.fa.filter(self.elem_math, self.doc)
        self.assertEqual(type(ret), pf.Math)
