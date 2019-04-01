"""Unit tests for Tikz2Svg."""

# pylint: disable=missing-docstring

from innoconv.extensions.tikz2svg import Tikz2Svg
from . import TestExtension

PATHS = (("Foo", ("foo",)),)


class TestTikz2Svg(TestExtension):
    """Test the Tikz2Svg extension."""

    @staticmethod
    def _run(extension=Tikz2Svg, ast=None, languages=("en",), paths=PATHS):
        _, [ast] = TestExtension._run(
            extension, ast, languages=languages, paths=paths
        )
        return ast
