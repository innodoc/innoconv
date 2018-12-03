"""Unit tests for GenerateToc."""

# pylint: disable=missing-docstring

from innoconv.extensions.generate_toc import GenerateToc
from innoconv.test.extensions import TestExtension, make_title


class TestGenerateToc(TestExtension):
    def test_generate_toc(self):
        generate_toc = self._run(GenerateToc)
        manifest = generate_toc._manifest  # pylint: disable=protected-access
        toc = manifest.toc
        self.assertIs(len(toc), 2)
        self.assertEqual(toc[0]['id'], 'title-1')
        self.assertEqual(toc[0]['title']['de'], make_title("Title 1", "de"))
        self.assertEqual(toc[0]['title']['en'], make_title("Title 1", "en"))
        self.assertEqual(toc[1]['id'], 'title-2')
        self.assertEqual(toc[1]['title']['de'], make_title("Title 2", "de"))
        self.assertEqual(toc[1]['title']['en'], make_title("Title 2", "en"))
        self.assertIs(len(toc[1]['children']), 1)
        self.assertEqual(toc[1]['children'][0]['id'], 'title-2-1')
        self.assertEqual(
            toc[1]['children'][0]['title']['de'],
            make_title("Title 2-1", "de"))
        self.assertEqual(
            toc[1]['children'][0]['title']['en'],
            make_title("Title 2-1", "en"))
