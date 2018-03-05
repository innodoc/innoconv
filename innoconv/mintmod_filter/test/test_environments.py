# pylint: disable=missing-docstring,invalid-name

import unittest
import panflute as pf
from innoconv.constants import ELEMENT_CLASSES
from innoconv.errors import NoPrecedingHeader
from innoconv.mintmod_filter.environments import Environments
from innoconv.mintmod_filter.elements import create_header


class TestEnvironments(unittest.TestCase):

    def setUp(self):
        self.doc = pf.Doc()
        self.environments = Environments()
        self.elem_content = r"""\begin{MSectionStart}
        Lorem ipsum.
        \end{MSectionStart}"""
        self.doc.content.extend(
            [pf.RawBlock(self.elem_content, format='latex')])
        self.elem = self.doc.content[0]  # this sets up elem.parent

    def test_msectionstart_no_header(self):
        "Should raise NoPrecedingHeader if there's no header"
        with self.assertRaises(NoPrecedingHeader):
            self.environments.handle_msectionstart(
                self.elem_content, [], self.elem)

    def test_msectionstart(self):
        "Should handle MSectionStart"

        # mock a preceding header
        create_header('foo', level=2, doc=self.elem.doc, auto_id=True)

        ret = self.environments.handle_msectionstart(
            self.elem_content, [], self.elem)

        self.assertIsInstance(ret, pf.Div)
        for cls in ELEMENT_CLASSES['MSECTIONSTART']:
            with self.subTest(cls=cls):
                self.assertIn(cls, ret.classes)  # pylint: disable=no-member


class TestContentBoxes(unittest.TestCase):

    def setUp(self):
        self.doc = pf.Doc()
        self.environments = Environments()

    def test_mxcontent(self):
        "MXContent"
        title = 'Foo content'
        self._test_content_box(
            self.environments.handle_mxcontent,
            ELEMENT_CLASSES['MXCONTENT'], title, [title], 'foo-content'
        )

    def test_handle_mexercises(self):
        "MExercises"
        self._test_content_box(
            self.environments.handle_mexercises,
            ELEMENT_CLASSES['MEXERCISES'], 'Aufgaben'
        )

    def test_handle_mexercise(self):
        "MExercise"
        self._test_content_box(
            self.environments.handle_mexercise,
            ELEMENT_CLASSES['MEXERCISE'], 'Aufgabe'
        )

    def test_handle_minfo(self):
        "MInfo"
        self._test_content_box(
            self.environments.handle_minfo,
            ELEMENT_CLASSES['MINFO'], 'Info'
        )

    def test_handle_mexperiment(self):
        "MExperiment"
        self._test_content_box(
            self.environments.handle_mexperiment,
            ELEMENT_CLASSES['MEXPERIMENT'], 'Experiment'
        )

    def test_handle_mexample(self):
        "MExample"
        self._test_content_box(
            self.environments.handle_mexample,
            ELEMENT_CLASSES['MEXAMPLE'], 'Beispiel'
        )

    def test_handle_mhint(self):
        "MHint"
        self._test_content_box(
            self.environments.handle_mhint,
            ELEMENT_CLASSES['MHINT'], None
        )

    def _test_content_box(self, handler, element_classes, title,
                          env_args=None, _id=''):
        """Test if content boxes (e.g. Exercises, Examples, Experiment, Info)
        are handled correctly
        """
        env_args = env_args or []

        # some latex content in the environment
        elem_content = r"""\begin{itemize}
        \item{item1}
        \item{item2}
        \end{itemize}"""

        # should return a div with the given classes
        self.doc.content.extend([pf.RawBlock(elem_content, format='latex')])
        elem = self.doc.content[0]  # this sets up elem.parent
        div = handler(elem_content, env_args, elem)
        self.assertIsInstance(div, pf.Div)
        self.assertEqual(div.classes, element_classes)
        for cls in element_classes:
            with self.subTest(cls=cls):
                self.assertIn(cls, div.classes)

        # should return a header with the correct title and id
        if title:
            self.assertIsInstance(div.content[0], pf.Header)
            self.assertEqual(div.content[0].identifier, _id)
            self.assertEqual(pf.stringify(div.content[0]), title)
            content_idx = 1
        else:
            content_idx = 0

        # and the content of the environment should be parsed correctly
        self.assertIsInstance(div.content[content_idx], pf.BulletList)
        self.assertEqual(div.content[content_idx].content[0].content[0]
                         .content[0].content[0].text, "item1")

        # TODO set and test a unique identifier to info boxes (and others)
