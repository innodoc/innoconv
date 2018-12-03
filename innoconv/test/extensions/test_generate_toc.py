"""Unit tests for GenerateToc."""

# pylint: disable=missing-docstring

from innoconv.extensions.generate_toc import GenerateToc
from innoconv.test.extensions import TestExtension, make_title

PATHS = (
    (None, ()),
    ("Title 1", ('title-1',)),
    ("Title 1-1", ('title-1', 'title-1-1')),
    ("Title 1-1-1", ('title-1', 'title-1-1', 'title-1-1-1')),
    ("Title 1-1-2", ('title-1', 'title-1-1', 'title-1-1-2')),
    ("Title 2", ('title-2',)),
    ("Title 2-1", ('title-2', 'title-2-1')),
)


class TestGenerateToc(TestExtension):
    def test_generate_toc(self):
        generate_toc = self._run(GenerateToc, paths=PATHS)
        manifest = generate_toc._manifest  # pylint: disable=protected-access
        toc = manifest.toc
        self.assertIs(len(toc), 2)
        self.assertEqual(toc[0]['id'], 'title-1')
        self.assertEqual(toc[0]['title']['de'], "Title 1 de")
        self.assertEqual(toc[0]['title']['en'], "Title 1 en")
        self.assertIs(len(toc[0]['children']), 1)
        self.assertEqual(toc[0]['children'][0]['id'], 'title-1-1')
        self.assertEqual(toc[0]['children'][0]['title']['de'], "Title 1-1 de")
        self.assertEqual(toc[0]['children'][0]['title']['en'], "Title 1-1 en")
        self.assertIs(len(toc[0]['children'][0]['children']), 2)
        self.assertEqual(toc[0]['children'][0]['children'][0]['id'], 'title-1-1-1')
        self.assertEqual(toc[0]['children'][0]['children'][0]['title']['de'], 'Title 1-1-1 de')
        self.assertEqual(toc[0]['children'][0]['children'][0]['title']['en'], 'Title 1-1-1 en')
        self.assertEqual(toc[0]['children'][0]['children'][1]['id'], 'title-1-1-2')
        self.assertEqual(toc[0]['children'][0]['children'][1]['title']['de'], 'Title 1-1-2 de')
        self.assertEqual(toc[0]['children'][0]['children'][1]['title']['en'], 'Title 1-1-2 en')
        self.assertEqual(toc[1]['id'], 'title-2')
        self.assertEqual(toc[1]['title']['de'], "Title 2 de")
        self.assertEqual(toc[1]['title']['en'], "Title 2 en")
        self.assertIs(len(toc[1]['children']), 1)
        self.assertEqual(toc[1]['children'][0]['id'], 'title-2-1')
        self.assertEqual(toc[1]['children'][0]['title']['de'], "Title 2-1 de")
        self.assertEqual(toc[1]['children'][0]['title']['en'], "Title 2-1 en")
