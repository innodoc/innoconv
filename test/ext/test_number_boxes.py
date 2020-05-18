"""Unit tests for NumberBoxes."""

from unittest.mock import call, patch

from innoconv.ext.number_boxes import NumberBoxes
from . import TestExtension
from ..utils import get_div_ast, get_filler_content, get_para_ast

AST = [
    get_para_ast(get_filler_content()),
    get_div_ast(classes="info"),
    get_para_ast(get_filler_content()),
    get_div_ast(classes="example", div_id="FOO_ID"),
    get_para_ast(get_filler_content()),
]


@patch("logging.warning")
class TestNumberBoxes(TestExtension):
    """Test the NumberBoxes extension."""

    def test_numbering(self, warning):
        """Test numbering."""
        number_boxes, _ = self._run(NumberBoxes, AST, languages=("en",))
        manifest_fields = number_boxes.manifest_fields()
        self.assertEqual(warning.call_count, 0)

        boxes = {
            "title-1": [("1.0.1", "info"), ("1.0.2", "example")],
            "title-2": [("2.0.1", "info"), ("2.0.2", "example")],
            "title-2/title-2-1": [("2.1.1", "info"), ("2.1.2", "example")],
        }
        self.assertEqual(manifest_fields["boxes"], boxes)

    def test_id_assignment(self, warning):
        """Test assignment of IDs."""
        _, asts = self._run(NumberBoxes, AST, languages=("en",))
        self.assertEqual(warning.call_count, 0)

        ast = asts[1]
        self.assertEqual(ast[1]["c"][0][0], "info-1.0.1")
        self.assertEqual(ast[1]["c"][0][2][0], ("data-number", "1.0.1"))
        self.assertEqual(ast[3]["c"][0][0], "FOO_ID")
        self.assertEqual(ast[3]["c"][0][2][0], ("data-number", "1.0.2"))

        ast = asts[2]
        self.assertEqual(ast[1]["c"][0][0], "info-2.0.1")
        self.assertEqual(ast[1]["c"][0][2][0], ("data-number", "2.0.1"))
        self.assertEqual(ast[3]["c"][0][0], "FOO_ID")
        self.assertEqual(ast[3]["c"][0][2][0], ("data-number", "2.0.2"))

        ast = asts[3]
        self.assertEqual(ast[1]["c"][0][0], "info-2.1.1")
        self.assertEqual(ast[1]["c"][0][2][0], ("data-number", "2.1.1"))
        self.assertEqual(ast[3]["c"][0][0], "FOO_ID")
        self.assertEqual(ast[3]["c"][0][2][0], ("data-number", "2.1.2"))

    def test_inconsistent_missing(self, warning):
        """Test detection of missing box."""
        number_boxes, _ = self._run(NumberBoxes, AST, languages=("en",))
        inconsistent_ast = AST[:3] + AST[4:]  # leave out one box
        self._run(number_boxes, inconsistent_ast, languages=("de",))
        self.assertEqual(warning.call_count, 3)
        for section_id in ("title-1", "title-2", "title-2/title-2-1"):
            self.assertIn(
                call("Section %s has too few boxes for language %s", section_id, "de"),
                warning.call_args_list,
            )

    def test_detect_inconsistent_extra(self, warning):
        """Test detection of extra box."""
        number_boxes, _ = self._run(NumberBoxes, AST, languages=("en",))
        inconsistent_ast = AST + [get_div_ast(classes="info")]
        self._run(number_boxes, inconsistent_ast, languages=("de",))
        self.assertEqual(warning.call_count, 3)
        for section_id, number in (
            ("title-1", "1.0.3"),
            ("title-2", "2.0.3"),
            ("title-2/title-2-1", "2.1.3"),
        ):
            self.assertIn(
                call(
                    "Section %s has extra box %s (%s) for language %s",
                    section_id,
                    number,
                    "info",
                    "de",
                ),
                warning.call_args_list,
            )
