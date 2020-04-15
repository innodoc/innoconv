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
        toc = generate_toc._toc  # pylint: disable=protected-access
        self.assertIs(len(toc), 2)
        self.assertEqual(toc[0]["id"], "title-1")
        self.assertEqual(toc[0]["title"]["de"], "Title 1 de")
        self.assertEqual(toc[0]["title"]["en"], "Title 1 en")
        self.assertIs(len(toc[0]["children"]), 1)
        self.assertEqual(toc[0]["children"][0]["id"], "title-1-1")
        self.assertEqual(toc[0]["children"][0]["title"]["de"], "Title 1-1 de")
        self.assertEqual(toc[0]["children"][0]["title"]["en"], "Title 1-1 en")
        self.assertIs(len(toc[0]["children"][0]["children"]), 2)
        self.assertEqual(toc[0]["children"][0]["children"][0]["id"], "title-1-1-1")
        self.assertEqual(
            toc[0]["children"][0]["children"][0]["title"]["de"], "Title 1-1-1 de",
        )
        self.assertEqual(
            toc[0]["children"][0]["children"][0]["title"]["en"], "Title 1-1-1 en",
        )
        self.assertEqual(toc[0]["children"][0]["children"][1]["id"], "title-1-1-2")
        self.assertEqual(
            toc[0]["children"][0]["children"][1]["title"]["de"], "Title 1-1-2 de",
        )
        self.assertEqual(
            toc[0]["children"][0]["children"][1]["title"]["en"], "Title 1-1-2 en",
        )
        self.assertEqual(toc[1]["id"], "title-2")
        self.assertEqual(toc[1]["title"]["de"], "Title 2 de")
        self.assertEqual(toc[1]["title"]["en"], "Title 2 en")
        self.assertIs(len(toc[1]["children"]), 1)
        self.assertEqual(toc[1]["children"][0]["id"], "title-2-1")
        self.assertEqual(toc[1]["children"][0]["title"]["de"], "Title 2-1 de")
        self.assertEqual(toc[1]["children"][0]["title"]["en"], "Title 2-1 en")

        manifest_fields = generate_toc.manifest_fields()
        self.assertIs(manifest_fields["toc"], toc)
