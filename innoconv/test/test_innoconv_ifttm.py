# pylint: disable=missing-docstring

import unittest
import panflute as pf
from innoconv.test.utils import get_pandoc_soup


class TestInnoconvIfttm(unittest.TestCase):
    def test_innoconv_ifttm(self):
        r"""Parse a whole tex document including \ifttm commands and check if
        output is correct."""
        soup = get_pandoc_soup('ifttm.tex', ['ifttm_filter.py'])
        paras = soup.find_all('p')
        self.assertEqual(len(paras), 3)
        para0_text = paras[0].get_text()
        self.assertEqual(para0_text, 'You can eat Apples if you want.')
        para1_text = paras[1].get_text()
        self.assertEqual(para1_text, 'Option 1')
        para2_text = paras[2].get_text()
        self.assertEqual(para2_text, 'Option A ')
