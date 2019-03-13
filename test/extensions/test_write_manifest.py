"""Unit tests for WriteManifest."""

# pylint: disable=missing-docstring

from unittest.mock import call, patch

from innoconv.extensions.write_manifest import WriteManifest
from innoconv.test.extensions import DEST, TestExtension


class TestWriteManifest(TestExtension):
    @patch('json.dump')
    @patch('builtins.open')
    def test_write_manifest(self, mock_open, mock_dump):
        self._run(WriteManifest)
        self.assertIs(mock_open.call_count, 1)
        self.assertEqual(
            mock_open.call_args, call('{}/manifest.json'.format(DEST), 'w'))
        self.assertIs(mock_dump.call_count, 1)
        manifest = mock_dump.call_args[0][0]
        self.assertEqual(manifest.title['en'], 'Title (en)')
        self.assertEqual(manifest.title['de'], 'Title (de)')
        self.assertEqual(manifest.languages, ('en', 'de'))
