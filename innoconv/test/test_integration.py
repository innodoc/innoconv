# pylint: disable=missing-docstring

import unittest
import panflute as pf
from innoconv.test.utils import get_doc_from_markup
from innoconv.utils import log

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

        log(doc.to_json())

        self.assertIsInstance(doc, pf.Doc)

        header1 = doc.content[0]
        self.assertIsInstance(header1, pf.Header)
        self.assertEqual(header1.identifier, 'label1')

        header2 = doc.content[1]
        self.assertIsInstance(header2, pf.Header)
        self.assertEqual(header2.identifier, 'label2')

        # content div header should receive id from \MLabel command
        content_div = doc.content[2]
        header3 = content_div.content[0]
        self.assertIsInstance(header3, pf.Header)
        self.assertEqual(header3.identifier, 'LABEL_BASE_SITE_ONE')

        # \MLabel command should be removed
        first_child = content_div.content[1]
        self.assertIsInstance(first_child, pf.Para)

        # Other label inside MXContent should be parsed
        another_label = first_child.content[2]
        self.assertIsInstance(another_label, pf.Span)
        self.assertIn('label', another_label.classes)
        self.assertEqual(another_label.identifier, 'label-paralabel')
