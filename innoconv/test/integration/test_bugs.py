# pylint: disable=missing-docstring

import unittest
import panflute as pf
from innoconv.test.utils import get_doc_from_markup


class TestCertainBugs(unittest.TestCase):

    def test_filename(self):
        """Underscore in filename should work."""
        tex = r"""
        \MUGraphicsSolo{bak_pop.png}{scale=1}{width:400px}
        """
        doc = get_doc_from_markup(tex)
        img = doc.content[0].content[0].content[0]
        self.assertIsInstance(img, pf.Image)
        self.assertEqual(img.url, 'bak_pop.png')
