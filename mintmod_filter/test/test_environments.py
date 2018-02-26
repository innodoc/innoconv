# pylint: disable=missing-docstring,invalid-name

import unittest
import panflute as pf
from mintmod_filter.constants import ELEMENT_CLASSES
from mintmod_filter.environments import Environments


class TestEnvironments(unittest.TestCase):

    def setUp(self):
        self.doc = pf.Doc()
        self.environments = Environments()

    def test_handle_minfo(self):
        self._test_content_box(
            self.environments.handle_minfo,
            ELEMENT_CLASSES['MINFO'], 'Info'
        )

    def test_handle_mexperiment(self):
        self._test_content_box(
            self.environments.handle_mexperiment,
            ELEMENT_CLASSES['MEXPERIMENT'], 'Experiment'
        )

    def test_handle_mexercise(self):
        self._test_content_box(
            self.environments.handle_mexercise,
            ELEMENT_CLASSES['MEXERCISE'], 'Aufgabe'
        )

    def test_handle_mexercises(self):
        self._test_content_box(
            self.environments.handle_mexercises,
            ELEMENT_CLASSES['MEXERCISES'], 'Aufgaben'
        )

    def test_handle_mexample(self):
        self._test_content_box(
            self.environments.handle_mexample,
            ELEMENT_CLASSES['MEXAMPLE'], 'Beispiel'
        )

    def _test_content_box(self, handler, element_classes, title):
        """Test if content boxes (e.g. Exercises, Examples, Experiment, Info)
        are handled correctly
        """
        # some latex content in the environment
        elem_content = r"""\begin{itemize}
        \item{item1}
        \item{item2}
        \end{itemize}"""

        # should return a div with the given classes
        self.doc.content.extend([pf.RawBlock(elem_content, format='latex')])
        elem = self.doc.content[0]  # this sets up elem.parent
        div = handler(elem_content, [], elem)
        self.assertIsInstance(div, pf.Div)
        self.assertEqual(div.classes, element_classes)

        # should return a header without an id but with the correct title
        self.assertIsInstance(div.content[0], pf.Header)
        self.assertEqual(div.content[0].identifier, "")
        self.assertEqual(div.content[0].content[0].text, title)

        # and the content of the environment should be parsed correctly
        self.assertIsInstance(div.content[1], pf.BulletList)
        self.assertEqual(div.content[1].content[0].content[0].content[0]
                         .content[0].text, "item1")

        # TODO set and test a unique identifier to info boxes (and others)
