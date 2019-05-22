"""Unit tests for AbstractExtension."""

import unittest

from innoconv.ext.abstract import AbstractExtension
from innoconv.manifest import Manifest

MANIFEST = Manifest({"title": {"en": "Foo Course Title"}, "languages": ("en",)})


class MyCrazyExtension(AbstractExtension):
    """Extension that serves for testing inheriting from AbstractExtension."""

    _helptext = "Foo bar"


class TestAbstractExtension(unittest.TestCase):
    """Test inheriting from AbstractExtension."""

    def test_helptext(self):
        """Test extension help text."""
        self.assertEqual(MyCrazyExtension.helptext(), "Foo bar")

    def test_methods(self):
        """Test extension method interface."""
        test_extension = MyCrazyExtension(MANIFEST)
        events = (
            "extension_list",
            "start",
            "pre_conversion",
            "pre_process_file",
            "post_process_file",
            "post_conversion",
            "finish",
        )
        for method_name in events:
            with self.subTest(method=method_name):
                self.assertTrue(callable(getattr(test_extension, method_name)))
