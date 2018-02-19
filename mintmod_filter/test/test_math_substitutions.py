import unittest
import panflute as pf
from mintmod_filter.math_substitutions import handle_math_substitutions


class TestHandleMathSubstitutions(unittest.TestCase):
    def test_handle_math_substitutions(self):
        elem_math = pf.Math(r'\N \R')
        doc = pf.Doc(pf.Block(elem_math))
        elem_math_repl = handle_math_substitutions(elem_math, doc)
        self.assertEqual(elem_math_repl.text, r'\mathbb{N} \mathbb{R}')
