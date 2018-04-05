# pylint: disable=missing-docstring

import unittest
import panflute as pf
from innoconv.test.utils import get_doc_from_markup
from innoconv.constants import INDEX_LABEL_PREFIX


class TestInnoconvIntegrationMlabel(unittest.TestCase):

    def test_msubsection(self):
        r"""Test if \MSubsection gets ID from \MLabel."""

        doc = get_doc_from_markup(r"""\MSubsection{My section}
        \MLabel{my-section-id}
        Blabla
        """)
        self.assertIsInstance(doc, pf.Doc)
        header = doc.content[0]
        self.assertIsInstance(header, pf.Header)
        self.assertEqual(header.identifier, 'my-section-id')
        self.assertIsInstance(doc.content[1], pf.Para)

    def test_minfo(self):
        r"""Test if \MInfo gets ID from \MLabel."""

        doc = get_doc_from_markup(r"""\begin{MInfo}
        \MLabel{VBKM01_Intervalle}
        Für zwei verschiedene reelle Zahlen betrachtet man insbesondere alle
        Zahlen.
        \end{MInfo}""")
        self.assertIsInstance(doc, pf.Doc)
        info_box = doc.content[0]
        self.assertIsInstance(info_box, pf.Div)
        self.assertEqual(info_box.identifier, 'VBKM01_Intervalle')

    def test_minfo_without_id(self):
        r"""\MInfo should not have ID without \MLabel."""

        doc = get_doc_from_markup(r"""\begin{MInfo}
        Foo bar
        \end{MInfo}""")
        self.assertIsInstance(doc, pf.Doc)
        info_box = doc.content[0]
        self.assertIsInstance(info_box, pf.Div)
        self.assertEqual(info_box.identifier, '')

    def test_mexample(self):
        r"""Test if \MExample gets ID from \MLabel."""

        doc = get_doc_from_markup(r"""\begin{MExample}
        \MLabel{great-example}
        Sind keine Klammern gesetzt, so wird $a^{p^q}$ als $a^{(p^q)}$
        interpretiert.
        \end{MExample}""")
        self.assertIsInstance(doc, pf.Doc)
        info_box = doc.content[0]
        self.assertIsInstance(info_box, pf.Div)
        self.assertEqual(info_box.identifier, 'great-example')

    def test_mexercises(self):
        r"""Test if \MExercises gets ID from \MLabel."""

        doc = get_doc_from_markup(r"""\begin{MExercises}
        \MLabel{VBKM01_AufgabenUmformen}
        Im folgenden \MSRef{VBKM01_AufgabenUmformen}{Aufgabenabschnitt} können
        Sie die Umformungstechniken an zahlreichen Aufgaben einüben.
        \end{MExercises}""")
        self.assertIsInstance(doc, pf.Doc)
        info_box = doc.content[0]
        self.assertIsInstance(info_box, pf.Div)
        self.assertEqual(info_box.identifier, 'VBKM01_AufgabenUmformen')

    def test_various(self):
        r"""Test if a latex string containing several \MLabel commands in
        different environments and positions are parsed correctly."""

        doc = get_doc_from_markup(r"""\MSubSection{foo}
            \MLabel{label1}

            \MTitle{header level 4}
            \MLabel{label2}

            \begin{MXContent}{Die erste Seite}{Seite 1}{STD}
            \MLabel{LABEL_BASE_SITE_ONE}

            Label: \MLabel{paralabel}
            \end{MXContent}""")

        self.assertIsInstance(doc, pf.Doc)

        header1 = doc.content[0]
        self.assertIsInstance(header1, pf.Header)
        self.assertEqual(header1.identifier, 'label1')

        header2 = doc.content[1]
        self.assertIsInstance(header2, pf.Header)
        self.assertEqual(header2.identifier, 'label2')

        # header for \MXContent should receive id from \MLabel command
        header3 = doc.content[2]
        self.assertIsInstance(header3, pf.Header)
        self.assertEqual(header3.identifier, 'LABEL_BASE_SITE_ONE')

        para = doc.content[3]

        # \MLabel command should be removed
        self.assertIsInstance(para, pf.Para)

        # Other label inside MXContent should be parsed
        another_label = para.content[2]
        self.assertIsInstance(another_label, pf.Span)
        self.assertIn(INDEX_LABEL_PREFIX, another_label.classes)
        self.assertEqual(another_label.identifier,
                         '{}-paralabel'.format(INDEX_LABEL_PREFIX))
