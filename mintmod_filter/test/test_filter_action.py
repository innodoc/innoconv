import unittest
import panflute as pf
from mintmod_filter.filter_action import filter_action


class TestFilterAction(unittest.TestCase):
    @classmethod
    def setUp(self):
        self.elem_str = pf.Str('foo')
        self.elem_math = pf.Math(r'1+2')
        self.doc = pf.Doc(pf.Block(self.elem_str, self.elem_math))

    def test_str_input(self):
        "filter_action() returns None if given Str element"
        ret = filter_action(self.elem_str, self.doc)
        self.assertIsNone(ret)

    def test_math_input(self):
        "filter_action() returns Math if given Math element"
        ret = filter_action(self.elem_math, self.doc)
        self.assertEqual(type(ret), pf.Math)
