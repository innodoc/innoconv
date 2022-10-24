"""Unit tests for innoconv.runner."""

import unittest
from unittest.mock import call, DEFAULT, patch

from innoconv.ext.abstract import AbstractExtension
from innoconv.manifest import Manifest
from innoconv.runner import InnoconvRunner

MANIFEST = Manifest(
    {
        "title": {"en": "Foo Course Title", "de": "Foo Kurstitel"},
        "languages": ("de", "en"),
        "min_score": 90,
        "pages": [
            {
                "id": "test1",
                "icon": "info-circle",
                "linked": ["nav"],
            },
            {"id": "test2"},
        ],
    }
)


def walk_side_effect(path):
    """Simulate a recursive traversal in an intact content directory."""
    lang = path[-2:]
    return iter(
        [
            (
                f"/src/{lang}",
                ["section-1", "section-2"],
                ["content.md"],
            ),
            (
                f"/src/{lang}/section-1",
                ["section-1.1", "section-1.2", "_static"],
                ["content.md"],
            ),
            (f"/src/{lang}/section-1/section-1.1", [], ["content.md"]),
            (f"/src/{lang}/section-1/section-1.2", [], ["content.md"]),
            (f"/src/{lang}/section-2", [], ["content.md"]),
        ]
    )


def walk_side_effect_missing_content_file(path):
    """Simulate a traversal with a content file missing."""
    lang = path[-2:]
    return iter([(f"/src/{lang}", ["section-1", "section-2"], [])])


def walk_side_effect_extra_section(path):
    """Simulate a traversal with an extra section for one language."""
    lang = path[-2:]
    if lang == "de":
        return iter(
            [
                ("/src/de", ["section-1"], ["content.md"]),
                ("/src/de/section-1", [], ["content.md"]),
            ]
        )
    return iter(
        [
            ("/src/en", ["section-1", "section-2"], ["content.md"]),
            ("/src/en/section-1", [], ["content.md"]),
            ("/src/en/section-2", [], ["content.md"]),
        ]
    )


def walk_side_effect_section_missing(path):
    """Simulate a traversal with a missing section for one language."""
    lang = path[-2:]
    if lang == "de":
        return iter(
            [
                ("/src/de", ["section-1", "section-2"], ["content.md"]),
                ("/src/de/section-1", [], ["content.md"]),
                ("/src/de/section-2", [], ["content.md"]),
            ]
        )
    return iter(
        [
            ("/src/en", ["section-1"], ["content.md"]),
            ("/src/en/section-1", [], ["content.md"]),
        ]
    )


def walk_side_effect_section_differs(path):
    """Simulate a traversal with different sections for both languages."""
    lang = path[-2:]
    if lang == "de":
        return iter(
            [
                ("/src/de", ["section-1", "section-2"], ["content.md"]),
                ("/src/de/section-1", [], ["content.md"]),
                ("/src/de/section-2", [], ["content.md"]),
            ]
        )
    return iter(
        [
            ("/src/en", ["section-1", "section-b"], ["content.md"]),
            ("/src/en/section-1", [], ["content.md"]),
            ("/src/en/section-b", [], ["content.md"]),
        ]
    )


TITLE = "Long title"
SHORT_TITLE = "Short"
SECTION_TYPE = "test"


@patch("builtins.open")
@patch(
    "innoconv.runner.to_ast",
    return_value=(["content_ast"], TITLE, SHORT_TITLE, SECTION_TYPE),
)
@patch("json.dump")
@patch("innoconv.runner.exists", return_value=True)
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
        _, makedirs, _, _, json_dump, *_ = args
        self.runner.run()

        paths = (
            # sections
            "/out/de",
            "/out/de/section-1",
            "/out/de/section-1/section-1.1",
            "/out/de/section-1/section-1.2",
            "/out/de/section-2",
            # pages
            "/out/de/_pages",
            "/out/de/_pages",
            # fragments
            "/out/de",
            "/out/de",
            # sections
            "/out/en",
            "/out/en/section-1",
            "/out/en/section-1/section-1.1",
            "/out/en/section-1/section-1.2",
            "/out/en/section-2",
            # pages
            "/out/en/_pages",
            "/out/en/_pages",
            # fragments
            "/out/en",
            "/out/en",
        )

        for i, path in enumerate(paths):
            with self.subTest(path):
                self.assertEqual(makedirs.call_args_list[i], call(path, exist_ok=True))
                self.assertEqual(json_dump.call_args_list[i][0][0], ["content_ast"])

        # assert no extra calls
        self.assertEqual(makedirs.call_count, len(paths))
        self.assertEqual(json_dump.call_count, len(paths))

    def test_run_no_folder(self, isdir, *_):
        """Ensure RuntimeError is raised on missing language folder."""
        isdir.return_value = False
        self.assertRaises(RuntimeError, self.runner.run)

    def test_run_content_file_missing(self, *args):
        """Ensure RuntimeError is raised on missing content file."""
        _, _, walk, *_ = args
        walk.side_effect = walk_side_effect_missing_content_file
        with self.assertRaises(RuntimeError):
            self.runner.run()

    def test_run_content_extra_section(self, *args):
        """Ensure RuntimeError is raised on extra section in one language."""
        _, _, walk, *_ = args
        walk.side_effect = walk_side_effect_extra_section
        with self.assertRaises(RuntimeError):
            self.runner.run()

    def test_run_content_section_missing(self, *args):
        """Ensure RuntimeError is raised if section missing in one language."""
        _, _, walk, *_ = args
        walk.side_effect = walk_side_effect_section_missing
        with self.assertRaises(RuntimeError):
            self.runner.run()

    def test_run_content_section_differs(self, *args):
        """Ensure RuntimeError is raised if a section differs."""
        _, _, walk, *_ = args
        walk.side_effect = walk_side_effect_section_differs
        with self.assertRaises(RuntimeError):
            self.runner.run()

    def test_run_to_ast_fails(self, *args):
        """Ensure RuntimeError is raised on failed AST conversion."""
        _, _, _, _, _, to_ast, *_ = args
        to_ast.side_effect = RuntimeError()
        with self.assertRaises(RuntimeError):
            self.runner.run()

    def test_run_no_pages(self, *_):
        """Ensure pages key can be missing from manifest."""
        manifest = Manifest(
            {"title": {"en": "Test"}, "languages": ("en",), "min_score": 90}
        )
        self.runner = InnoconvRunner("/src", "/out", manifest, [])
        try:
            self.runner.run()
        except RuntimeError:
            self.fail("Exception was raised with missing pages key!")


@patch("builtins.open")
@patch("innoconv.runner.EXTENSIONS", {"my_ext": AbstractExtension})
@patch(
    "innoconv.runner.to_ast",
    return_value=(["content_ast"], TITLE, SHORT_TITLE, SECTION_TYPE),
)
@patch("json.dump")
@patch("innoconv.runner.exists", return_value=True)
@patch("innoconv.runner.walk", side_effect=walk_side_effect)
@patch("innoconv.runner.makedirs")
@patch("innoconv.runner.isdir", return_value=True)
@patch("innoconv.ext.abstract.AbstractExtension.__init__", return_value=None)
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
        "innoconv.ext.abstract.AbstractExtension",
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

        pre_process_file_args = [
            # sections
            "de",
            "de/section-1",
            "de/section-1/section-1.1",
            "de/section-1/section-1.2",
            "de/section-2",
            # 2x page
            "de/_pages",
            "de/_pages",
            # 2x footer
            "de",
            "de",
            # sections
            "en",
            "en/section-1",
            "en/section-1/section-1.1",
            "en/section-1/section-1.2",
            "en/section-2",
            # 2x page
            "en/_pages",
            "en/_pages",
            # 2x footer
            "en",
            "en",
        ]

        # pre_process_file hooks
        for i, arg in enumerate(pre_process_file_args):
            self.assertEqual(mocks["pre_process_file"].call_args_list[i], call(arg))

        # assert no extra calls
        self.assertEqual(
            mocks["post_process_file"].call_count, len(pre_process_file_args)
        )

        # post_process_file hooks: sections
        for i in list(range(0, 5)) + list(range(9, 14)):
            self.assertEqual(
                mocks["post_process_file"].call_args_list[i],
                call(["content_ast"], TITLE, "section", "test", "Short"),
            )

        # post_process_file hooks: pages
        for i in (5, 6, 14, 15):
            self.assertEqual(
                mocks["post_process_file"].call_args_list[i],
                call(["content_ast"], TITLE, "page", None),
            )

        # post_process_file hooks: fragments
        for i in (7, 8, 16, 17):
            self.assertEqual(
                mocks["post_process_file"].call_args_list[i],
                call(["content_ast"], TITLE, "fragment", None),
            )

        self.assertEqual(mocks["post_conversion"].call_count, 2)
        self.assertEqual(mocks["post_conversion"].call_args_list[0], call("de"))
        self.assertEqual(mocks["post_conversion"].call_args_list[1], call("en"))

        self.assertEqual(mocks["finish"].call_count, 1)
