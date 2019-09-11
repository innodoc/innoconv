"""Unit tests for IndexTerms."""

from innoconv.ext.index_terms import IndexTerms
from . import TestExtension
from ..utils import get_filler_content, get_index_term, get_para_ast

AST = [
    get_para_ast(get_index_term(get_filler_content(), "Term A")),
    get_para_ast(get_index_term(get_filler_content(), "Term A")),
    get_para_ast(get_index_term(get_filler_content(), "Term B")),
]


class TestIndexTerms(TestExtension):
    """Test the IndexTerms extension."""

    def test_index_terms_ids(self):
        """Test assignment of IDs."""
        _, asts = self._run(IndexTerms, AST, languages=("en",))
        for ast in asts:
            self.assertEqual(ast[0]["c"]["c"][0][0], "index-term-term-a-0")
            self.assertEqual(ast[1]["c"]["c"][0][0], "index-term-term-a-1")
            self.assertEqual(ast[2]["c"]["c"][0][0], "index-term-term-b-0")

    def test_index_terms_manifest_fields(self):
        """Test index_terms manifest field."""
        index_terms, _ = self._run(IndexTerms, AST, languages=("en",))
        manifest_fields = index_terms.manifest_fields()
        index_terms_field = {
            "en": {
                "term-a": [
                    "Term A",
                    [
                        ["", "term-a-0"],
                        ["", "term-a-1"],
                        ["title-1", "term-a-0"],
                        ["title-1", "term-a-1"],
                        ["title-2", "term-a-0"],
                        ["title-2", "term-a-1"],
                        ["title-2/title-2-1", "term-a-0"],
                        ["title-2/title-2-1", "term-a-1"],
                    ],
                ],
                "term-b": [
                    "Term B",
                    [
                        ["", "term-b-0"],
                        ["title-1", "term-b-0"],
                        ["title-2", "term-b-0"],
                        ["title-2/title-2-1", "term-b-0"],
                    ],
                ],
            }
        }
        self.assertEqual(manifest_fields["index_terms"], index_terms_field)
