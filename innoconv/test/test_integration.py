# pylint: disable=missing-docstring

import unittest
import panflute as pf
from innoconv.test.utils import get_doc_from_markup

TEX_MLABEL = r"""\MSubSection{foo}
\MLabel{label1}

\MTitle{header level 4}
\MLabel{label2}

\begin{MXContent}{Die erste Seite}{Seite 1}{STD}
\MLabel{LABEL_BASE_SITE_ONE}

Label: \MLabel{paralabel}
\end{MXContent}"""


class TestInnoconvIntegration(unittest.TestCase):

    def test_labels(self):
        """Test if a latex string containing several `MLabel` commands in
        different environments and positions are parsed correctly."""

        doc = get_doc_from_markup(TEX_MLABEL)

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
        self.assertIn('label', another_label.classes)
        self.assertEqual(another_label.identifier, 'label-paralabel')
