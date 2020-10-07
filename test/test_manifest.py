"""Unit tests for innoconv.manifest."""

import unittest
from unittest.mock import call, mock_open, patch

import yaml

from innoconv.manifest import Manifest

MINIMUM = """
title:
  de: Foo Titel
  en: Foo Title
languages: [en, de]
min_score: 80
"""

KEYWORDS = f"""{MINIMUM}
keywords: [foo, bar, baz]
"""

MISSING_TITLE = """
languages: [en, de]
"""

MISSING_LANGUAGES = """
title:
  de: Foo Titel
  en: Foo Title
"""


@patch("builtins.open", new_callable=mock_open, read_data=MINIMUM)
class TestManifestFromDirectory(unittest.TestCase):
    """Test the from_directory class method."""

    def test_yml_ext(self, mopen):
        """Ensure a manifest.yml is accepted."""
        manifest = Manifest.from_directory("/path/to/content")
        self.assertIsInstance(manifest, Manifest)
        self.assertEqual(mopen.call_args, call("/path/to/content/manifest.yml", "r"))

    def test_yaml_ext(self, mopen):
        """Ensure a manifest.yaml is accepted."""
        mopen.side_effect = (
            FileNotFoundError,
            mock_open(read_data=MINIMUM).return_value,
        )
        manifest = Manifest.from_directory("/path/to/content")
        self.assertIsInstance(manifest, Manifest)
        self.assertEqual(
            mopen.call_args_list,
            [
                call("/path/to/content/manifest.yml", "r"),
                call("/path/to/content/manifest.yaml", "r"),
            ],
        )

    def test_not_found(self, mopen):
        """Ensure a FileNotFoundError is raised if no manifest was found."""
        mopen.side_effect = (FileNotFoundError, FileNotFoundError)
        with self.assertRaises(FileNotFoundError):
            Manifest.from_directory("/path/to/content")

    def test_invalid_yaml(self, mopen):
        """Ensure a YAMLError is raised if manifest could not be parsed."""
        invalid_yaml = '"This is no valid yaml'
        mopen.side_effect = (mock_open(read_data=invalid_yaml).return_value,)
        with self.assertRaises(yaml.YAMLError):
            Manifest.from_directory("/path/to/content")


class TestManifestFromYaml(unittest.TestCase):
    """Test the from_yaml class method."""

    def test_minimum(self):
        """Test the minium example."""
        manifest = Manifest.from_yaml(MINIMUM)
        title = getattr(manifest, "title")
        self.assertIs(len(title), 2)
        self.assertEqual(title["de"], "Foo Titel")
        self.assertEqual(title["en"], "Foo Title")
        languages = getattr(manifest, "languages")
        self.assertIs(len(languages), 2)
        self.assertIn("en", languages)
        self.assertIn("de", languages)
        self.assertIs(getattr(manifest, "min_score"), 80)
        with self.assertRaises(AttributeError):
            getattr(manifest, "keywords")
        with self.assertRaises(AttributeError):
            getattr(manifest, "custom_content")

    def test_keywords(self):
        """Test a manifest with keywords."""
        manifest = Manifest.from_yaml(KEYWORDS)
        keywords = getattr(manifest, "keywords")
        self.assertIs(len(keywords), 3)
        self.assertIn("foo", keywords)
        self.assertIn("bar", keywords)
        self.assertIn("baz", keywords)

    def test_missing_required(self):
        """Ensure a RuntimeError is raised for missing data."""
        for data in (MISSING_TITLE, MISSING_LANGUAGES):
            with self.subTest(data):
                with self.assertRaises(RuntimeError):
                    Manifest.from_yaml(data)
