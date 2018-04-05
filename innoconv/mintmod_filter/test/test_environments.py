# pylint: disable=missing-docstring,invalid-name

import unittest
import panflute as pf
from innoconv.constants import ELEMENT_CLASSES
from innoconv.errors import NoPrecedingHeader
from innoconv.mintmod_filter.environments import Environments
from innoconv.mintmod_filter.elements import create_header


class TestMsectionStart(unittest.TestCase):

    def setUp(self):
        self.doc = pf.Doc()
        self.environments = Environments()
        self.elem_content = r"""
        \begin{MSectionStart}
            Lorem ipsum
        \end{MSectionStart}"""
        self.doc.content.extend(
            [pf.RawBlock(self.elem_content, format='latex')])
        self.elem = self.doc.content[0]  # this sets up elem.parent

    def test_msectionstart_no_header(self):
        """handle_msectionstart should raise NoPrecedingHeader if there's no
        header"""
        with self.assertRaises(NoPrecedingHeader):
            self.environments.handle_msectionstart(
                'Lorem ipsum', [], self.elem)

    def test_msectionstart(self):
        """Should handle MSectionStart"""

        # mock a preceding header
        create_header('foo', level=2, doc=self.elem.doc)

        ret = self.environments.handle_msectionstart(
            'Lorem ipsum', [], self.elem)

        self.assertIsInstance(ret, pf.Div)

        header = ret.content[0]
        self.assertIsInstance(header, pf.Header)
        self.assertEqual(pf.stringify(header), 'foo')

        para = ret.content[1]
        self.assertIsInstance(para.content[0], pf.Str)
        self.assertIsInstance(para.content[1], pf.Space)
        self.assertIsInstance(para.content[2], pf.Str)
        self.assertEqual(para.content[0].text, 'Lorem')
        self.assertEqual(para.content[2].text, 'ipsum')

        for cls in ELEMENT_CLASSES['MSECTIONSTART']:
            with self.subTest(cls=cls):
                self.assertIn(cls, ret.classes)  # pylint: disable=no-member


class TestMxContent(unittest.TestCase):

    def setUp(self):
        self.doc = pf.Doc()
        self.environments = Environments()
        self.elem_content = r"""
        \begin{MXContent}{Nice title}{Short title}{STD}
            Lorem ipsum
        \end{MXContent}"""
        self.doc.content.extend(
            [pf.RawBlock(self.elem_content, format='latex')])
        self.elem = self.doc.content[0]  # this sets up elem.parent

    def test_mxcontent(self):
        """Should handle MXContent"""
        ret = self.environments.handle_mxcontent(
            'Foo bar', ['Nice title', 'Short title', 'STD'], self.elem)

        self.assertIsInstance(ret, list)

        header = ret[0]
        self.assertIsInstance(header, pf.Header)
        self.assertEqual(pf.stringify(header), 'Nice title')

        para = ret[1]
        self.assertIsInstance(para.content[0], pf.Str)
        self.assertIsInstance(para.content[1], pf.Space)
        self.assertIsInstance(para.content[2], pf.Str)
        self.assertEqual(para.content[0].text, 'Foo')
        self.assertEqual(para.content[2].text, 'bar')


class TestBoxesWithoutTitle(unittest.TestCase):

    def setUp(self):
        self.doc = pf.Doc()
        self.environments = Environments()

    def test_handle_mexercises(self):
        """MExercises"""
        self._test_content_box(
            self.environments.handle_mexercises, ELEMENT_CLASSES['MEXERCISES'])

    def test_handle_mexercise(self):
        """MExercise"""
        self._test_content_box(
            self.environments.handle_mexercise, ELEMENT_CLASSES['MEXERCISE'])

    def test_handle_minfo(self):
        """MInfo"""
        self._test_content_box(
            self.environments.handle_minfo, ELEMENT_CLASSES['MINFO'])

    def test_handle_mexperiment(self):
        """MExperiment"""
        self._test_content_box(self.environments.handle_mexperiment,
                               ELEMENT_CLASSES['MEXPERIMENT'])

    def test_handle_mexample(self):
        """MExample"""
        self._test_content_box(
            self.environments.handle_mexample, ELEMENT_CLASSES['MEXAMPLE'])

    def test_handle_mhint(self):
        """MHint"""
        self._test_content_box(
            self.environments.handle_mhint, ELEMENT_CLASSES['MHINT'])

    def _test_content_box(self, handler, element_classes, env_args=None):
        # some latex content in the environment
        elem_content = r"""
            \begin{itemize}
                \item{item1}
                \item{item2}
            \end{itemize}
        """

        # should return a div with the given classes
        self.doc.content.extend([pf.RawBlock(elem_content, format='latex')])
        elem = self.doc.content[0]  # this sets up elem.parent
        div = handler(elem_content, env_args, elem)
        self.assertIsInstance(div, pf.Div)
        self.assertEqual(div.classes, element_classes)
        for cls in element_classes:
            with self.subTest(cls=cls):
                self.assertIn(cls, div.classes)

        # and the content of the environment should be parsed correctly
        bullet_list = div.content[0]
        self.assertIsInstance(bullet_list, pf.BulletList)
        self.assertEqual(bullet_list.content[0].content[0].content[0]
                         .content[0].text, 'item1')
