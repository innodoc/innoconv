"""Unit tests for innoconv.__main__"""

# pylint: disable=missing-docstring

import unittest

from innoconv.extensions.abstract import AbstractExtension
from innoconv.test.utils import get_manifest

MANIFEST = get_manifest()


class TestExtension(AbstractExtension):
    # pylint: disable=W0223
    _helptext = "Foo bar"


class TestAbstractExtension(unittest.TestCase):
    def test_helptext(self):
        self.assertEqual(TestExtension.helptext(), "Foo bar")

    def test_notimplemented(self):
        test_extension = TestExtension(MANIFEST)
        events = (
            ('start', ('source', 'output')),
            ('pre_conversion', ('en',)),
            ('pre_process_file', ('relpath',)),
            ('post_process_file', (['ast'], ['Foo Title'])),
            ('process_ast_array', (['ast'], None)),
            ('process_ast_element', ({'ast': 'element', 't': 'Type'}, 'Type',
                                     None)),
            ('post_conversion', ('en',)),
            ('finish', ()),
        )
        for method_name, method_args in events:
            with self.subTest(method=method_name):
                with self.assertRaises(NotImplementedError):
                    func = getattr(test_extension, method_name)
                    func(*method_args)
