"""Unit tests for innoconv.utils."""

import unittest
from unittest.mock import MagicMock, Mock, patch

from innoconv.utils import to_ast


def patch_popen(returncode=0, output=""):
    """Patch Popen with custom return code and stdout output."""

    def decorator(func):
        @patch(
            target="innoconv.utils.Popen",
            return_value=MagicMock(
                __enter__=Mock(
                    return_value=Mock(
                        returncode=returncode,
                        communicate=Mock(return_value=(output.encode(), "".encode())),
                    )
                )
            ),
        )
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


class TestToAst(unittest.TestCase):
    """Test to_ast() utility function mocking away pandoc functionality."""

    @patch_popen(
        output=(
            '{"blocks":[{"t":"Para","c":[]}],'
            '"meta":{"title":{"t":"MetaInlines","c":[{"t":"Str","c":"Test"},'
            '{"t":"Space"},{"t":"Str","c":"Title"}]},'
            '"short_title":{"t":"MetaInlines","c":[{"t":"Str","c":"Test"}]}}}'
        ),
    )
    def test_to_ast(self, popen_mock):
        """Ensure pandoc is called."""
        blocks, title, short_title, section_type = to_ast("/some/document.md")
        self.assertTrue(popen_mock.called)
        self.assertEqual(blocks, [{"t": "Para", "c": []}])
        self.assertEqual(title, "Test Title")
        self.assertEqual(short_title, "Test")
        self.assertIsNone(section_type)

    @patch_popen(returncode=255)
    def test_to_ast_fails(self, _):
        """Ensure a RuntimeError is raised when pandoc fails."""
        with self.assertRaises(RuntimeError):
            to_ast("/some/document.md")

    @patch_popen(
        output=(
            '{"blocks":[{"t":"Para","c":[]}],"meta":'
            '{"title":{"t":"MetaInlines","c":[{"t":"Str","c":"Test"}]}}}'
        )
    )
    def test_to_ast_no_short_title(self, _):
        """Check run without short title."""
        try:
            *_, short_title, _ = to_ast("/some/document.md")
        except ValueError:
            self.fail("to_ast() raised ValueError!")
        self.assertEqual(short_title, "Test")

    @patch_popen(output='{"blocks":[{"t":"Para","c":[]}],"meta":{}}')
    def test_to_ast_fails_without_title(self, _):
        """Ensure a ValueError is raised when title is missing."""
        with self.assertRaises(ValueError):
            to_ast("/some/document.md")

    @patch_popen(output='{"blocks":[{"t":"Para","c":[]}],"meta":{}}')
    def test_ignore_missing_title(self, _):
        """Ensure no Error is raised when title is missing."""
        try:
            to_ast("/some/document.md", ignore_missing_title=True)
        except ValueError:
            self.fail("to_ast() raised ValueError!")

    @patch_popen(
        output=(
            '{"blocks":[{"t":"Para","c":[]}],'
            '"meta":{"title":{"t":"MetaInlines","c":[{"t":"Str","c":"Test"},'
            '{"t":"Space"},{"t":"Str","c":"Title"}]},'
            '"type":{"t":"MetaInlines","c":[{"t":"Str","c":"exercises"}]}}}'
        )
    )
    def test_extract_section_type(self, popen_mock):
        """Ensure section type is extracted."""
        _, __, ___, section_type = to_ast("/some/document.md")
        self.assertTrue(popen_mock.called)
        self.assertEqual(section_type, "exercises")
