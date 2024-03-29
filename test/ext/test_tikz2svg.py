"""Unit tests for Tikz2Svg."""

from copy import deepcopy
from hashlib import md5
from os.path import join
from unittest.mock import MagicMock, Mock, patch

from innoconv.ext.tikz2svg import (
    Tikz2Svg,
    TIKZ_FILENAME,
    TIKZ_FOLDER,
    TIKZ_IMG_TAG_ALT,
)
from innoconv.manifest import Manifest
from . import TestExtension
from ..utils import get_image_ast, get_para_ast


PATHS = (("Foo", ("foo",)),)
TIKZ_STRING = r"""
\begin{tikzpicture}[x=1.0cm, y=1.0cm]
    \draw[thick, black] (-5.2,0) -- (6.2,0);
    \foreach \x in {-5, -4, ..., 6}
        \draw[shift={(\x,0)},color=black] (0pt,6pt) -- (0pt,-6pt)
    node[below=1.5pt] {\normalsize $\x$};
\\end{tikzpicture}
"""
TIKZ_BLOCK = {"t": "CodeBlock", "c": [["", ["tikz"], []], TIKZ_STRING]}
TIKZ_HASH = md5(TIKZ_STRING.strip().encode()).hexdigest()
TIKZ_PREAMBLE = r"""
\mycrazypreamble
"""

IMAGE_BLOCK = get_image_ast(
    join(TIKZ_FOLDER, f"{TIKZ_FILENAME.format(TIKZ_HASH)}.svg"),
    description="TikZ Image",
)


@patch("innoconv.ext.tikz2svg.scour")
@patch(
    "innoconv.ext.tikz2svg.open",
    return_value=MagicMock(
        __enter__=Mock(return_value=Mock(read=Mock(return_value="<svg></svg>")))
    ),
)
@patch(
    "innoconv.ext.tikz2svg.TemporaryDirectory",
    return_value=MagicMock(__enter__=Mock(return_value="")),
)
@patch("innoconv.ext.tikz2svg.makedirs")
@patch(
    "innoconv.ext.tikz2svg.Popen",
    return_value=MagicMock(__enter__=Mock(return_value=Mock(returncode=0))),
)
class TestTikz2Svg(TestExtension):
    """Test the Tikz2Svg extension."""

    def test_simple_life_cycle(
        self, mock_popen, mock_mkdir, mock_td, mock_open, mock_scour
    ):
        """Test successful lifecycle."""
        input_ast = [deepcopy(TIKZ_BLOCK)]
        _, asts = self._run(Tikz2Svg, input_ast, languages=("en",), paths=PATHS)
        self.assertTrue(mock_open.called)
        self.assertTrue(mock_scour.scourString.called)
        self.assertTrue(mock_td.called)
        self.assertTrue(mock_mkdir.called)
        self.assertEqual(mock_popen.call_count, 2)
        image = asts[0][0]
        self.assertEqual(image["t"], "Image")
        filename = f"{TIKZ_FILENAME.format(TIKZ_HASH)}.svg"
        imgpath = f"{TIKZ_FOLDER}/{filename}"
        self.assertEqual(image["c"][2][0], imgpath)
        self.assertEqual(image["c"][2][1], TIKZ_IMG_TAG_ALT)

    def test_with_caption(self, *_):
        """Test conversion with caption."""
        input_ast = [
            {
                "c": [["", ["figure"], []], [get_para_ast(), deepcopy(TIKZ_BLOCK)]],
                "t": "Div",
            }
        ]
        _, asts = self._run(Tikz2Svg, input_ast, languages=("en",), paths=PATHS)
        div = asts[0][0]
        self.assertEqual(div["t"], "Div")
        self.assertIn("figure", div["c"][0][1])
        image = div["c"][1][0]
        self.assertEqual(image["t"], "Image")
        self.assertEqual(image["c"][1][0]["c"], "Lorem Ipsum")

    def test_with_preamble(self, mock_popen, *_):
        """Test conversion with LaTeX preamble."""
        manifest_data = {
            "languages": ("en",),
            "title": {"en": "Foo"},
            "min_score": 90,
            "tikz_preamble": TIKZ_PREAMBLE,
        }
        manifest = Manifest(manifest_data)
        input_ast = [deepcopy(TIKZ_BLOCK)]
        self._run(Tikz2Svg, input_ast, paths=PATHS, manifest=manifest)
        pipe_mock = mock_popen.return_value.__enter__.return_value
        self.assertIn(TIKZ_PREAMBLE, pipe_mock.stdin.write.call_args[0][0].decode())

    def test_no_tikz_images(self, *_):
        """Test without any TikZ images."""
        input_ast = [{"c": [{"t": "Str", "c": "Foo"}]}]
        _, asts = self._run(
            Tikz2Svg, deepcopy(input_ast), languages=("en",), paths=PATHS
        )
        self.assertEqual(asts[0], input_ast)

    def test_conversion_error(self, mock_popen, *_):
        """Test failed conversion."""
        rc_orig = mock_popen.return_value.__enter__.return_value.returncode
        try:
            mock_popen.return_value.__enter__.return_value.returncode = 1
            input_ast = [deepcopy(TIKZ_BLOCK)]
            with self.assertRaises(RuntimeError):
                self._run(Tikz2Svg, input_ast, languages=("en",), paths=PATHS)
        finally:
            mock_popen.return_value.__enter__.return_value.returncode = rc_orig
