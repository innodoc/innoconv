"""Unit tests for innoconv.__main__"""

# pylint: disable=missing-docstring

import unittest

from innoconv.extensions.abstract import AbstractExtension


class TestExtension(AbstractExtension):
    # pylint: disable=W0223
    _helptext = "Foo bar"


class TestAbstractExtension(unittest.TestCase):
    def test_helptext(self):
        self.assertEqual(TestExtension.helptext(), "Foo bar")

    def test_notimplemented(self):
        test_extension = TestExtension()
        events = (
            ('init', ('en', '', '')),
            ('pre_conversion', ('en',)),
            ('pre_process_file', ('relpath',)),
            ('post_process_file', (['ast'], 'Foo Title')),
            ('post_conversion', ('en',)),
            ('finish', ()),
        )
        for method_name, method_args in events:
            with self.subTest(method=method_name):
                with self.assertRaises(NotImplementedError):
                    func = getattr(test_extension, method_name)
                    func(*method_args)
