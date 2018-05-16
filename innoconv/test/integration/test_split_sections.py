# pylint: disable=missing-docstring,too-many-locals

import unittest
import os
import json
import tempfile
from innoconv.test.utils import get_doc_from_markup


class TestSplitSections(unittest.TestCase):

    def test_split_sections(self):
        """test postflight split_sections"""
        tex = r"""
\MSection{1}
\MLabel{LABEL_1}

\begin{MSectionStart}
Einführungstext-für-header-1.
\end{MSectionStart}

\MSubsection{1-1}
\MLabel{LABEL_1_1}

\begin{MIntro}
\MLabel{LABEL_1_1_1}
MIntro-text-hier.
\end{MIntro}

\MSubsection{1-2}
\MLabel{LABEL_1_2}

subsection-text-hier.

\MSubsubsection{1-2-1}
\MLabel{LABEL_1_2_1}

subsubsection-text-hier.
"""
        langs = (
            ('de', 'Einführung', 'einfuhrung'),
            ('en', 'Introduction', 'introduction'),
        )
        for lang in langs:
            with self.subTest(lang=lang):
                lang_code, intro_title, intro_id = lang
                with tempfile.TemporaryDirectory() as tmpdir:
                    pandoc_output = os.path.join(tmpdir, 'output.json')
                    get_doc_from_markup(tex,
                                        style='innoconv-split',
                                        output=pandoc_output,
                                        lang=lang_code)

                    toc_output = os.path.join(tmpdir, lang_code, 'toc.json')
                    with open(toc_output, 'r') as toc_file:
                        toc = json.load(toc_file)

                        sec_1 = toc[0]
                        self.assertEqual(sec_1['id'], 'LABEL_1')
                        self.assertEqual(sec_1['title'][0]['c'], '1')

                        sec_1_1 = sec_1['children'][0]
                        self.assertEqual(sec_1_1['id'], 'LABEL_1_1')
                        self.assertEqual(sec_1_1['title'][0]['c'], '1-1')

                        sec_1_1_1 = sec_1_1['children'][0]
                        self.assertEqual(sec_1_1_1['id'], intro_id)
                        self.assertEqual(
                            sec_1_1_1['title'][0]['c'], intro_title)

                        sec_1_2 = sec_1['children'][1]
                        self.assertEqual(sec_1_2['id'], 'LABEL_1_2')
                        self.assertEqual(sec_1_2['title'][0]['c'], '1-2')

                        sec_1_2_1 = sec_1_2['children'][0]
                        self.assertEqual(sec_1_2_1['id'], 'LABEL_1_2_1')
                        self.assertEqual(sec_1_2_1['title'][0]['c'], '1-2-1')
