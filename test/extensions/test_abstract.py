"""Unit tests for AbstractExtension."""

import unittest

from innoconv.extensions.abstract import AbstractExtension
from innoconv.manifest import Manifest

MANIFEST = Manifest({"title": {"en": "Foo Course Title"}, "languages": ("en",)})


class MyCrazyExtension(AbstractExtension):
    """Extension that serves for testing inheriting from AbstractExtension."""

    # pylint: disable=abstract-method
    _helptext = "Foo bar"


class TestAbstractExtension(unittest.TestCase):
    """Test inheriting from AbstractExtension."""

    def test_helptext(self):
        """Test extension help text."""
        self.assertEqual(MyCrazyExtension.helptext(), "Foo bar")

    def test_notimplemented(self):
        """Test extension method interface."""
        test_extension = MyCrazyExtension(MANIFEST)
        events = (
            ("start", ("source", "output")),
            ("pre_conversion", ("en",)),
            ("pre_process_file", ("relpath",)),
            ("post_process_file", (["ast"], ["Foo Title"])),
            ("post_conversion", ("en",)),
            ("finish", ()),
        )
        for method_name, method_args in events:
            with self.subTest(method=method_name):
                with self.assertRaises(NotImplementedError):
                    func = getattr(test_extension, method_name)
                    func(*method_args)
