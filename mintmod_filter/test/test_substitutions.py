# pylint: disable=missing-docstring,invalid-name

import unittest
import panflute as pf
from mintmod_filter.substitutions import handle_math_substitutions


class TestHandleSubstitutions(unittest.TestCase):
    def test_handle_math_substitutions(self):
        elem_math = pf.Math(r'\N \R')
        elem_math_repl = handle_math_substitutions(elem_math)
        self.assertEqual(elem_math_repl.text, r'\mathbb{N} \mathbb{R}')
