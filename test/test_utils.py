"""Unit tests for innoconv.utils."""

import unittest
from unittest.mock import Mock, patch

from innoconv.utils import to_ast

PROCESS_MOCK = Mock()


def _config_process_mock(returncode, output):
    PROCESS_MOCK.returncode = returncode
    PROCESS_MOCK.communicate.return_value = output.encode(), "".encode()


@patch("innoconv.utils.Popen", return_value=PROCESS_MOCK)
class TestToAst(unittest.TestCase):
    """Test to_ast() utility function mocking away pandoc functionality."""

    def test_to_ast(self, popen_mock):
        """Ensure pandoc is called."""
        pandoc_output = (
            '{"blocks":[{"t":"Para","c":[]}],"meta":{"title":'
            '{"t":"MetaInlines","c":[{"t":"Str","c":"Test"},'
            '{"t":"Space"},{"t":"Str","c":"Title"}]}}}'
        )
        _config_process_mock(0, pandoc_output)
        blocks, title = to_ast("/some/document.md")
        self.assertTrue(popen_mock.called)
        self.assertEqual(blocks, [{"t": "Para", "c": []}])
        self.assertEqual(title, "Test Title")

    def test_to_ast_fails(self, _):
        """Ensure a RuntimeError is raised when pandoc fails."""
        _config_process_mock(255, "")
        with self.assertRaises(RuntimeError):
            to_ast("/some/document.md")

    def test_to_ast_fails_without_title(self, _):
        """Ensure a ValueError is raised when title is missing."""
        pandoc_output = '{"blocks":[{"t":"Para","c":[]}],"meta":{}}'
        _config_process_mock(0, pandoc_output)
        with self.assertRaises(ValueError):
            to_ast("/some/document.md")
