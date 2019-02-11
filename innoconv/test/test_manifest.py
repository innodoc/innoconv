"""Unit tests for innoconv.manifest"""

# pylint: disable=missing-docstring

import json
import unittest

from innoconv.manifest import Manifest, ManifestEncoder

MINIMUM = """
title:
  de: Foo Titel
  en: Foo Title
languages: [en, de]
"""

CUSTOM_CONTENT = MINIMUM + """
custom_content:
  license: '_license'
  contributors: '_contributors'
"""

KEYWORDS = MINIMUM + """
keywords: [foo, bar, baz]
"""

TIKZ = MINIMUM + """
tikz_preamble: 'tikz_'
"""

MISSING_TITLE = """
languages: [en, de]
"""

MISSING_LANGUAGES = """
title:
  de: Foo Titel
  en: Foo Title
"""


class TestManifestFromYaml(unittest.TestCase):
    def test_minimum(self):
        manifest = Manifest.from_yaml(MINIMUM)
        title = getattr(manifest, 'title')
        self.assertIs(len(title), 2)
        self.assertEqual(title['de'], 'Foo Titel')
        self.assertEqual(title['en'], 'Foo Title')
        languages = getattr(manifest, 'languages')
        self.assertIs(len(languages), 2)
        self.assertIn('en', languages)
        self.assertIn('de', languages)
        with self.assertRaises(AttributeError):
            getattr(manifest, 'keywords')
        with self.assertRaises(AttributeError):
            getattr(manifest, 'custom_content')

    def test_custom_content(self):
        manifest = Manifest.from_yaml(CUSTOM_CONTENT)
        custom_content = getattr(manifest, 'custom_content')
        self.assertIs(len(custom_content), 2)
        self.assertEqual(custom_content['license'], '_license')
        self.assertEqual(custom_content['contributors'], '_contributors')

    def test_keywords(self):
        manifest = Manifest.from_yaml(KEYWORDS)
        keywords = getattr(manifest, 'keywords')
        self.assertIs(len(keywords), 3)
        self.assertIn('foo', keywords)
        self.assertIn('bar', keywords)
        self.assertIn('baz', keywords)

    def test_tikz(self):
        manifest = Manifest.from_yaml(TIKZ)
        self.assertTrue(hasattr(manifest, 'tikz_preamble'))
        tikz_preamble = getattr(manifest, 'tikz_preamble')
        self.assertEqual('tikz_', tikz_preamble)

    def test_missing_required(self):
        for data in (MISSING_TITLE, MISSING_LANGUAGES):
            with self.subTest(data):
                with self.assertRaises(RuntimeError):
                    Manifest.from_yaml(data)


class TestManifestEncoder(unittest.TestCase):
    def test_encoder(self):
        manifest = Manifest.from_yaml(KEYWORDS)
        manifest_str = json.dumps(manifest, cls=ManifestEncoder)
        manifest_dict = json.loads(manifest_str)
        self.assertEqual(manifest_dict['languages'], ['en', 'de'])
        self.assertEqual(manifest_dict['title']['de'], 'Foo Titel')
        self.assertEqual(manifest_dict['title']['en'], 'Foo Title')
        self.assertEqual(manifest_dict['keywords'], ['foo', 'bar', 'baz'])
        self.assertNotIn('custom_content', manifest_dict)

    def test_encoder_skip_innoconv_only_fields(self):
        manifest = Manifest.from_yaml(TIKZ)
        manifest_str = json.dumps(manifest, cls=ManifestEncoder)
        manifest_dict = json.loads(manifest_str)
        self.assertIn('languages', manifest_dict)
        self.assertIn('title', manifest_dict)
        self.assertNotIn('tikz_preamble', manifest_dict)

    def test_encoder_fail(self):
        class Foo():
            pass
        with self.assertRaises(TypeError):
            json.dumps(Foo(), cls=ManifestEncoder)
