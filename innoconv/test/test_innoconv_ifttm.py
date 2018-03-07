# pylint: disable=missing-docstring

import unittest
from innoconv.test.utils import get_pandoc_soup


class TestInnoconvIfttm(unittest.TestCase):
    def test_innoconv_ifttm(self):
        soup = get_pandoc_soup('ifttm.tex', ['ifttm_filter.py'])
        paras = soup.find_all('p')
        self.assertEqual(len(paras), 1)
        text = paras[0].get_text()
        self.assertEqual(text, 'You can eat Apples if you want.')
