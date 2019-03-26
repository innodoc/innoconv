"""Unit tests for WriteManifest."""

import unittest
from unittest.mock import call, patch

from innoconv.extensions.write_manifest import WriteManifest
from . import DEST, TestExtension


class TestWriteManifest(TestExtension):
    """Test the WriteManifest extension."""

    @patch("json.dump")
    @patch("builtins.open")
    def test_write_manifest(self, mock_open, mock_dump):
        """Test the creation of a manifest file in the destination directory."""
        self._run(WriteManifest)
        self.assertIs(mock_open.call_count, 1)
        self.assertEqual(
            mock_open.call_args, call("{}/manifest.json".format(DEST), "w")
        )
        self.assertIs(mock_dump.call_count, 1)
        manifest = mock_dump.call_args[0][0]
        self.assertEqual(manifest.title["en"], "Title (en)")
        self.assertEqual(manifest.title["de"], "Title (de)")
        self.assertEqual(manifest.languages, ("en", "de"))

    # TODO: implement missing test (#41)
    @unittest.skip("TODO")
    def test_write_manifest_ignore_fields(self, mock_open, mock_dump):
        """Ensure specific fields are ignored in output manifest."""
