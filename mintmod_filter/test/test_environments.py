import unittest
import panflute as pf
from mintmod_filter.environments import Environments,\
    MINFO_CLASSES, MEXPERIMENT_CLASSES, MEXERCISE_CLASSES


class TestEnvironments(unittest.TestCase):

    def setUp(self):
        self.environments = Environments()
        self.doc = pf.Doc()

    def test_handle_minfo(self):
        self._handle_content_box(
            self.environments.handle_minfo,
            MINFO_CLASSES, 'Info'
        )

    def test_handle_mexperiment(self):
        self._handle_content_box(
            self.environments.handle_mexperiment,
            MEXPERIMENT_CLASSES, 'Experiment'
        )

    def test_handle_mexercise(self):
        self._handle_content_box(
            self.environments.handle_mexercise,
            MEXERCISE_CLASSES, 'Aufgabe'
        )

    def _handle_content_box(self, command, div_classes, title):
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
        self.assertEquals(div.classes, div_classes)

        # it should return a header without an id but with the correct title
        self.assertIsInstance(div.content[0], pf.Header)
        self.assertEquals(div.content[0].identifier, "")
        self.assertEquals(div.content[0].content[0].text, title)

        # and the content of the environment should be parsed correctly
        self.assertIsInstance(div.content[1], pf.BulletList)
        self.assertEquals(div.content[1].content[0].content[0]
                             .content[0].content[0].text, "item1")

        # TODO set and test a unique identifier to info boxes (and others)
