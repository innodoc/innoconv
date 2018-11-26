"""Unit tests for tikz2pdf extension"""

# pylint: disable=missing-docstring

import unittest
import copy
import os

from innoconv.extensions.tikz2pdf import Tikz2Pdf
from innoconv.constants import STATIC_FOLDER, TIKZ_FOLDER, TIKZ_FILENAME

TIKZSTRING = ("\\begin{tikzpicture}[x=1.0cm, y=1.0cm] \n"
              "\\draw[thick, black] (-5.2,0) -- (6.2,0);\n"
              "\\foreach \\x in {-5, -4, ..., 6}\n"
              "\\draw[shift={(\\x,0)},color=black] (0pt,6pt) -- (0pt,-6pt) "
              "node[below=1.5pt] {\\normalsize $\\x$};\n"
              "\\end{tikzpicture}\n")

TIKZBLOCK = {
    "t": "CodeBlock",
    "c": [
        [
            "",
            ["tikz"],
            []
        ],
        TIKZSTRING
    ]
}

IMAGEBLOCK = {
    "t": "Image",
    "c": [
        [
            "",
            [],
            []
        ],
        [
            {
                "t": "Str",
                "c": TIKZSTRING
            }
        ],
        [
            os.path.join(STATIC_FOLDER, TIKZ_FOLDER, TIKZ_FILENAME.format(0)),
            ""
        ]
    ]
}


TESTPATH = "~/TEMP"  # "/homes/mathphys/insam/TEMP/a"


class TestTikz2Pdf(unittest.TestCase):

    def __init__(self, arg):
        super(TestTikz2Pdf, self).__init__(arg)
        self.tikz2pdf = Tikz2Pdf()

    def test_replace_block(self):
        self.tikz2pdf.tikz_images = list()
        block = copy.deepcopy(TIKZBLOCK)
        self.tikz2pdf.replace_tikz_element(block)
        self.assertEqual(block, IMAGEBLOCK)
        self.assertIn(TIKZSTRING, self.tikz2pdf.tikz_images)

    def test_conversion(self):
        self.tikz2pdf.tikz_images = list()
        self.tikz2pdf.tikz_images.append(TIKZSTRING)
        self.tikz2pdf.output_dir_base = TESTPATH
        self.tikz2pdf.finish()

    def test_simple_life_cycle(self):
        block = copy.deepcopy(TIKZBLOCK)
        self.tikz2pdf.init(['de'], 'SOURCE', TESTPATH)
        self.tikz2pdf.pre_conversion('de')
        self.tikz2pdf.pre_process_file('de/path/example')
        self.tikz2pdf.post_process_file([{'c': [block]}], 'example')
        self.tikz2pdf.post_conversion('de')
        self.tikz2pdf.finish()
        self.assertEqual(IMAGEBLOCK, block)
