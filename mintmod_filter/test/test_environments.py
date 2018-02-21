import unittest
import panflute as pf
from mintmod_filter.constants import CSS_CLASSES
from mintmod_filter.environments import Environments


class TestEnvironments(unittest.TestCase):

    def setUp(self):
        self.environments = Environments()
        self.doc = pf.Doc()

    def test_handle_minfo(self):
        self._test_content_box(
            self.environments.handle_minfo,
            CSS_CLASSES['MINFO'], 'Info'
        )

    def test_handle_mexperiment(self):
        self._test_content_box(
            self.environments.handle_mexperiment,
            CSS_CLASSES['MEXPERIMENT'], 'Experiment'
        )

    def test_handle_mexercise(self):
        self._test_content_box(
            self.environments.handle_mexercise,
            CSS_CLASSES['MEXERCISE'], 'Aufgabe'
        )

    def test_handle_mexercises(self):
        self._test_content_box(
            self.environments.handle_mexercises,
            CSS_CLASSES['MEXERCISES'], 'Aufgaben'
        )

    def test_handle_mexample(self):
        self._test_content_box(
            self.environments.handle_mexample,
            CSS_CLASSES['MEXAMPLE'], 'Beispiel'
        )

    def _test_content_box(self, command, css_classes, title):
        """Test if content boxes (e.g. Exercises, Examples, Experiment, Info)
        are handled correctly
        """
        # some latex content in the environment
        elem_content = r"""\begin{itemize}
        \item{item1}
        \item{item2}
        \end{itemize}"""

        # the handling of the env should return a div with the given classes
        div = command(elem_content, [], self.doc)
        self.assertIsInstance(div, pf.Div)
        self.assertEqual(div.classes, css_classes)

        # it should return a header without an id but with the correct title
        self.assertIsInstance(div.content[0], pf.Header)
        self.assertEqual(div.content[0].identifier, "")
        self.assertEqual(div.content[0].content[0].text, title)

        # and the content of the environment should be parsed correctly
        self.assertIsInstance(div.content[1], pf.BulletList)
        self.assertEqual(div.content[1].content[0].content[0].content[0]
                         .content[0].text, "item1")

        # TODO set and test a unique identifier to info boxes (and others)
