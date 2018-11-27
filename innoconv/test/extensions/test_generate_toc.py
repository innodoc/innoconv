"""Unit tests for GenerateToc."""

# pylint: disable=missing-docstring

from innoconv.extensions.generate_toc import GenerateToc
from innoconv.test.extensions import TestExtension


class TestGenerateToc(TestExtension):
    def test_generate_toc(self):
        generate_toc = self._run(GenerateToc)
        manifest = generate_toc._manifest  # pylint: disable=protected-access
        toc_de = manifest.toc['de']
        self.assertIs(len(toc_de), 2)
        self.assertEqual(toc_de[0]['id'], 'title-1')
        self.assertEqual(toc_de[0]['title'], "Title 1 de")
        self.assertEqual(toc_de[1]['id'], 'title-2')
        self.assertEqual(toc_de[1]['title'], "Title 2 de")
        self.assertIs(len(toc_de[1]['children']), 1)
        self.assertEqual(toc_de[1]['children'][0]['id'], 'title-2-1')
        self.assertEqual(toc_de[1]['children'][0]['title'], "Title 2-1 de")
        toc_en = manifest.toc['en']
        self.assertIs(len(toc_en), 2)
        self.assertEqual(toc_en[0]['id'], 'title-1')
        self.assertEqual(toc_en[0]['title'], "Title 1 en")
        self.assertEqual(toc_en[1]['id'], 'title-2')
        self.assertEqual(toc_en[1]['title'], "Title 2 en")
        self.assertIs(len(toc_en[1]['children']), 1)
        self.assertEqual(toc_en[1]['children'][0]['id'], 'title-2-1')
        self.assertEqual(toc_en[1]['children'][0]['title'], "Title 2-1 en")
