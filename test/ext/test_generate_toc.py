"""Unit tests for GenerateToc."""

from innoconv.ext.generate_toc import GenerateToc
from . import TestExtension

PATHS = (
    (None, ()),
    ("Title 1", ("title-1",)),
    ("Title 1-1", ("title-1", "title-1-1")),
    ("Title 1-1-1", ("title-1", "title-1-1", "title-1-1-1")),
    ("Title 1-1-2", ("title-1", "title-1-1", "title-1-1-2")),
    ("Title 2", ("title-2",)),
    ("Title 2-1", ("title-2", "title-2-1")),
)


class TestGenerateToc(TestExtension):
    """Test the GenerateToc extension."""

    def test_generate_toc(self):
        """Test the TOC generation for a section tree."""
        generate_toc, _ = self._run(GenerateToc, paths=PATHS)
        toc = generate_toc.manifest_fields()["toc"]

        self.assertIs(len(toc), 2)

        title_1, title_2 = toc
        title_1_1 = title_1["children"][0]
        title_1_1_1, title_1_1_2 = title_1_1["children"]
        title_2_1 = title_2["children"][0]

        self.assertEqual(title_1["id"], "title-1")
        self.assertEqual(title_1["title"]["de"], "Title 1 de")
        self.assertEqual(title_1["title"]["en"], "Title 1 en")
        self.assertIs(len(title_1["children"]), 1)

        self.assertEqual(title_1_1["id"], "title-1-1")
        self.assertEqual(title_1_1["title"]["de"], "Title 1-1 de")
        self.assertEqual(title_1_1["title"]["en"], "Title 1-1 en")
        self.assertIs(len(title_1_1["children"]), 2)

        self.assertEqual(title_1_1_1["id"], "title-1-1-1")
        self.assertEqual(title_1_1_1["title"]["de"], "Title 1-1-1 de")
        self.assertEqual(title_1_1_1["title"]["en"], "Title 1-1-1 en")
        self.assertNotIn("children", title_1_1_1)

        self.assertEqual(title_1_1_2["id"], "title-1-1-2")
        self.assertEqual(title_1_1_2["title"]["de"], "Title 1-1-2 de")
        self.assertEqual(title_1_1_2["title"]["en"], "Title 1-1-2 en")
        self.assertNotIn("children", title_1_1_2)

        self.assertEqual(title_2["id"], "title-2")
        self.assertEqual(title_2["title"]["de"], "Title 2 de")
        self.assertEqual(title_2["title"]["en"], "Title 2 en")
        self.assertIs(len(title_2["children"]), 1)

        self.assertEqual(title_2_1["id"], "title-2-1")
        self.assertEqual(title_2_1["title"]["de"], "Title 2-1 de")
        self.assertEqual(title_2_1["title"]["en"], "Title 2-1 en")
        self.assertNotIn("children", title_2_1)
