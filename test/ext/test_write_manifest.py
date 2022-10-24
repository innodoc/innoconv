"""Unit tests for WriteManifest."""

from unittest.mock import call, patch

from innoconv.ext.abstract import AbstractExtension
from innoconv.ext.write_manifest import WriteManifest
from innoconv.manifest import Manifest
from . import DEST, TestExtension


@patch("json.dump")
@patch("builtins.open")
class TestWriteManifest(TestExtension):
    """Test the WriteManifest extension."""

    def test_write_manifest(self, mock_open, mock_dump):
        """Test the creation of a manifest file in the destination directory."""
        self._run(WriteManifest)
        self.assertIs(mock_open.call_count, 1)
        self.assertEqual(
            mock_open.call_args, call(f"{DEST}/manifest.json", "w", encoding="utf-8")
        )
        self.assertIs(mock_dump.call_count, 1)
        manifest_dict = mock_dump.call_args[0][0]
        self.assertEqual(manifest_dict["title"]["en"], "Title (en)")
        self.assertEqual(manifest_dict["title"]["de"], "Title (de)")
        self.assertEqual(manifest_dict["languages"], ("en", "de"))

    def test_custom_field(self, _, mock_dump):
        """Test inclusion of custom field from other extension."""
        # pylint: disable=abstract-method

        class ExtA(AbstractExtension):
            """Extension that does not write custom fields."""

        class ExtB(AbstractExtension):
            """Extension that writes a custom field."""

            @staticmethod
            def manifest_fields():
                """Provide custom manifest field."""
                return {"otherfield": "foo bar"}

        languages = ("en", "de")
        manifest = Manifest(
            {
                "languages": languages,
                "title": {"en": "Title", "de": "Titel"},
                "min_score": 90,
            }
        )
        ext = WriteManifest(manifest)
        ext.extension_list([ExtA(manifest), ExtB(manifest)])
        self._run(ext, languages=languages, manifest=manifest)
        manifest_dict = mock_dump.call_args[0][0]
        self.assertEqual(manifest_dict["otherfield"], "foo bar")
