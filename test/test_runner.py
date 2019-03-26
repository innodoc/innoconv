"""Unit tests for innoconv.runner."""

import unittest
from unittest.mock import call, DEFAULT, patch

from innoconv.extensions.abstract import AbstractExtension
from innoconv.manifest import Manifest
from innoconv.runner import InnoconvRunner

MANIFEST = Manifest(
    {
        "title": {"en": "Foo Course Title", "de": "Foo Kurstitel"},
        "languages": ("de", "en"),
    }
)


def walk_side_effect(path):
    """Simulate a recursive traversal in an intact content directory."""
    lang = path[-2:]
    return iter(
        [
            (
                "/src/{}".format(lang),
                ["section-1", "section-2"],
                ["content.md"],
            ),
            (
                "/src/{}/section-1".format(lang),
                ["section-1.1", "section-1.2", "_static"],
                ["content.md"],
            ),
            ("/src/{}/section-1/section-1.1".format(lang), [], ["content.md"]),
            ("/src/{}/section-1/section-1.2".format(lang), [], ["content.md"]),
            ("/src/{}/section-2".format(lang), [], ["content.md"]),
        ]
    )


def walk_side_effect_error(path):
    """Simulate a traversal in a defective content directory."""
    lang = path[-2:]
    return iter([("/src/{}".format(lang), ["section-1", "section-2"], [])])


TITLE = [
    {"t": "Str", "c": "Section"},
    {"t": "Space"},
    {"t": "Str", "c": "title"},
]


@patch("builtins.open")
@patch("innoconv.runner.to_ast", return_value=(["content_ast"], TITLE))
@patch("json.dump")
@patch("innoconv.runner.walk", side_effect=walk_side_effect)
@patch("innoconv.runner.makedirs")
@patch("innoconv.runner.isdir", return_value=True)
class TestInnoconvRunner(unittest.TestCase):
    """Test the InnoconvRunner lifecycle."""

    def setUp(self):
        """Instantiate the runner instance."""
        self.runner = InnoconvRunner("/src", "/out", MANIFEST, [])

    def test_run(self, *args):
        """Test a regular run. Assert directory and file creation."""
        _, makedirs, _, json_dump, *_ = args
        self.runner.run()

        self.assertEqual(makedirs.call_count, 10)
        self.assertEqual(json_dump.call_count, 10)

        paths = (
            "/out/de",
            "/out/de/section-1",
            "/out/de/section-1/section-1.1",
            "/out/de/section-1/section-1.2",
            "/out/de/section-2",
            "/out/en",
            "/out/en/section-1",
            "/out/en/section-1/section-1.1",
            "/out/en/section-1/section-1.2",
            "/out/en/section-2",
        )

        for i, path in enumerate(paths):
            with self.subTest(path):
                self.assertEqual(
                    makedirs.call_args_list[i], call(path, exist_ok=True)
                )
                self.assertEqual(
                    json_dump.call_args_list[i][0][0], ["content_ast"]
                )

    def test_run_no_folder(self, isdir, *_):
        """Ensure RuntimeError is raised on missing language folder."""
        isdir.return_value = False
        self.assertRaises(RuntimeError, self.runner.run)

    def test_run_content_file_missing(self, *args):
        """Ensure RuntimeError is raised on missing content file."""
        _, _, walk, *_ = args
        walk.side_effect = walk_side_effect_error
        with self.assertRaises(RuntimeError):
            self.runner.run()

    def test_run_to_ast_fails(self, *args):
        """Ensure RuntimeError is raised on failed AST conversion."""
        _, _, _, _, to_ast, *_ = args
        to_ast.side_effect = RuntimeError()
        with self.assertRaises(RuntimeError):
            self.runner.run()


@patch("builtins.open")
@patch("innoconv.runner.EXTENSIONS", {"my_ext": AbstractExtension})
@patch("innoconv.runner.to_ast", return_value=(["content_ast"], TITLE))
@patch("json.dump")
@patch("innoconv.runner.walk", side_effect=walk_side_effect)
@patch("innoconv.runner.makedirs")
@patch("innoconv.runner.isdir", return_value=True)
@patch(
    "innoconv.extensions.abstract.AbstractExtension.__init__", return_value=None
)
class TestInnoconvRunnerExtensions(unittest.TestCase):
    """Test runner interfacing properly with extensions."""

    def test_valid_ext(self, init, *_):
        """Ensure a valid extension is accepted."""
        extensions = ("my_ext",)
        InnoconvRunner("/src", "/out", MANIFEST, extensions)
        self.assertIsInstance(init.call_args[0][0], Manifest)

    def test_invalid_ext(self, *_):
        """Ensure a RuntimeError is raised for an unknown extension."""
        extensions = ("my_ext", "extension_does_not_exist")
        with self.assertRaises(RuntimeError):
            InnoconvRunner("/src", "/out", MANIFEST, extensions)

    @patch.multiple(
        "innoconv.extensions.abstract.AbstractExtension",
        start=DEFAULT,
        pre_conversion=DEFAULT,
        pre_process_file=DEFAULT,
        post_process_file=DEFAULT,
        post_conversion=DEFAULT,
        finish=DEFAULT,
    )
    def test_notify_ext(self, *_, **mocks):
        """Test the whole runner lifecycle extension event flow."""
        extensions = ("my_ext",)
        runner = InnoconvRunner("/src", "/out", MANIFEST, extensions)
        runner.run()

        self.assertEqual(mocks["start"].call_count, 1)
        self.assertEqual(mocks["start"].call_args, call("/out", "/src"))

        self.assertEqual(mocks["pre_conversion"].call_count, 2)
        self.assertEqual(mocks["pre_conversion"].call_args_list[0], call("de"))
        self.assertEqual(mocks["pre_conversion"].call_args_list[1], call("en"))

        self.assertEqual(mocks["pre_process_file"].call_count, 10)
        self.assertEqual(
            mocks["pre_process_file"].call_args_list[0], call("de")
        )
        self.assertEqual(
            mocks["pre_process_file"].call_args_list[1], call("de/section-1")
        )
        self.assertEqual(
            mocks["pre_process_file"].call_args_list[2],
            call("de/section-1/section-1.1"),
        )
        self.assertEqual(
            mocks["pre_process_file"].call_args_list[3],
            call("de/section-1/section-1.2"),
        )
        self.assertEqual(
            mocks["pre_process_file"].call_args_list[4], call("de/section-2")
        )
        self.assertEqual(
            mocks["pre_process_file"].call_args_list[5], call("en")
        )
        self.assertEqual(
            mocks["pre_process_file"].call_args_list[6], call("en/section-1")
        )
        self.assertEqual(
            mocks["pre_process_file"].call_args_list[7],
            call("en/section-1/section-1.1"),
        )
        self.assertEqual(
            mocks["pre_process_file"].call_args_list[8],
            call("en/section-1/section-1.2"),
        )
        self.assertEqual(
            mocks["pre_process_file"].call_args_list[9], call("en/section-2")
        )

        self.assertEqual(mocks["post_process_file"].call_count, 10)
        for i in range(0, 10):
            self.assertEqual(
                mocks["post_process_file"].call_args_list[i],
                call(["content_ast"], TITLE),
            )

        self.assertEqual(mocks["post_conversion"].call_count, 2)
        self.assertEqual(mocks["post_conversion"].call_args_list[0], call("de"))
        self.assertEqual(mocks["post_conversion"].call_args_list[1], call("en"))

        self.assertEqual(mocks["finish"].call_count, 1)
