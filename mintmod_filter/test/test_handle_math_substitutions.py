import unittest
import panflute as pf
from mintmod_filter.handle_math_substitutions import handle_math_substitutions


class TestHandleMathSubstitutions(unittest.TestCase):
    def setUp(self):
        self.elem_math = pf.Math(r'\N \R')
        self.doc = pf.Doc(pf.Block(self.elem_math))

    def test_handle_math_substitutions(self):
        elem_math = handle_math_substitutions(self.elem_math, self.doc)
        self.assertEqual(elem_math.text, r'\mathbb{N} \mathbb{R}')
