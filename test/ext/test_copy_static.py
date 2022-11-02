"""Unit tests for CopyStatic."""

import itertools
from os.path import join
from unittest.mock import call, patch

from innoconv.constants import STATIC_FOLDER
from innoconv.ext.copy_static import CopyStatic
from . import DEST, PATHS, SOURCE, TestExtension
from ..utils import (
    get_complex_ast,
    get_generic_link_ast,
    get_image_ast,
    get_para_ast,
    get_video_ast,
    get_youtube_ast,
)


def _is_file_mock_no_logo(filename):
    if "_logo" in filename:
        return False
    return True


def _is_file_mock_logo_svg(filename):
    if "_logo.svg" in filename and "/en/" not in filename:
        return True
    return False


def _is_file_mock_present_localized(filename):
    if "present.jpg" in filename and "/en/" in filename:
        return True
    return False


def _is_file_mock_present_non_localized(filename):
    if "present.jpg" in filename and "/en/" not in filename:
        return True
    return False


def _is_file_mock_only_en(filename):
    if "_logo" in filename:
        return False
    if "/en/" in filename:
        return True
    if "/la/" in filename:
        return False
    return True


def _is_file_mock_non_localized(filename):
    if "_logo" in filename or "/en/" in filename:
        return False
    return True


@patch("os.makedirs", return_value=True)
@patch("os.path.lexists", return_value=True)
@patch("os.path.isfile", side_effect=_is_file_mock_no_logo)
@patch("shutil.copyfile")
class TestCopyStatic(TestExtension):
    """Test the CopyStatic extension."""

    def test_logo(self, copyfile, isfile, *_):
        """Test logo copy."""
        isfile.side_effect = _is_file_mock_logo_svg
        copy_static, _ = self._run(CopyStatic, [], languages=("en",))
        self.assertEqual(copyfile.call_count, 1)
        self.assertIn(
            call(
                join(SOURCE, STATIC_FOLDER, "_logo.svg"),
                join(DEST, STATIC_FOLDER, "_logo.svg"),
            ),
            copyfile.call_args_list,
        )
        manifest_fields = copy_static.manifest_fields()
        self.assertEqual(manifest_fields["logo"], "file:_logo.svg")

    def test_no_logo(self, copyfile, *_):
        """Test logo copy."""
        copy_static, _ = self._run(CopyStatic, [], languages=("en",))
        self.assertEqual(copyfile.call_count, 0)
        manifest_fields = copy_static.manifest_fields()
        self.assertNotIn("logo", manifest_fields)

    def test_absolute_localized(self, copyfile, isfile, *_):
        """Test an absolute, localized file path."""
        isfile.side_effect = _is_file_mock_present_localized
        ast = [get_image_ast("/present.jpg")]
        _, asts = self._run(CopyStatic, ast, languages=("en",))
        self.assertEqual(copyfile.call_count, 1)
        self.assertIn(
            call(
                join(SOURCE, "en", STATIC_FOLDER, "present.jpg"),
                join(DEST, STATIC_FOLDER, "_en", "present.jpg"),
            ),
            copyfile.call_args_list,
        )
        for i, path in enumerate(PATHS):
            with self.subTest(path):
                self.assertEqual(asts[i][0]["c"][2][0], "_en/present.jpg")

    def test_absolute_nonlocalized(self, copyfile, isfile, *_):
        """Test an absolute, non-localized file path."""
        isfile.side_effect = _is_file_mock_present_non_localized
        ast = [get_image_ast("/present.jpg")]
        _, asts = self._run(CopyStatic, ast, languages=("en",))
        self.assertEqual(copyfile.call_count, 1)
        src = join(SOURCE, STATIC_FOLDER, "present.jpg")
        dst = join(DEST, STATIC_FOLDER, "present.jpg")
        self.assertEqual(call(src, dst), copyfile.call_args)
        for i, path in enumerate(PATHS):
            with self.subTest(path):
                self.assertEqual(asts[i][0]["c"][2][0], "present.jpg")

    def test_example(self, copyfile, *_):
        """Test a somewhat complex example."""
        _, asts = self._run(CopyStatic, get_complex_ast(), languages=("en",))
        self.assertEqual(copyfile.call_count, 11)
        for i, (title, path) in enumerate(PATHS):
            with self.subTest((title, path)):
                jpath = f"{'/'.join(path)}/" if path else ""
                self.assertEqual(asts[i][1]["c"][0]["c"][2][0], "_en/present.png")
                self.assertEqual(
                    asts[i][2]["c"][0]["c"][0]["c"][2][0],
                    "_en/subfolder/present.mp4",
                )
                self.assertEqual(asts[i][3]["c"][2]["c"][2][0], "_en/localizable.gif")
                self.assertEqual(
                    asts[i][3]["c"][3]["c"][2][0],
                    f"_en/{jpath}example_video.ogv",
                )
                self.assertEqual(
                    asts[i][4]["c"][2][0], "https://www.example.com/example.png"
                )
                self.assertEqual(
                    asts[i][5]["c"][0]["c"][1][0]["c"][2][0],
                    f"_en/{jpath}example_image.jpg",
                )

    def test_file_does_not_exist(self, *args):
        """Ensure raising of RuntimeError for non-existing file references."""
        _, isfile, _, _ = args
        isfile.side_effect = itertools.cycle((False,))
        tests = (
            ("/not-present.png", [get_image_ast("/not-present.png")]),
            ("/not-present.mp4", [get_video_ast("/not-present.mp4")]),
            ("/single_language.svg", [get_image_ast("/single_language.svg")]),
        )
        for name, ast in tests:
            with self.subTest(name):
                with self.assertRaises(RuntimeError):
                    self._run(CopyStatic, ast)

    def test_ignore_remote(self, copyfile, *_):
        """Ensure ignoring of remote image references."""
        tests = (
            "http://www.example.com/example.png",
            "http://www.example.com/example.png",
            "ftp://ftp.example.com/example.png",
        )
        for addr in tests:
            with self.subTest(addr):
                self._run(CopyStatic, [get_image_ast(addr)])
                self.assertEqual(copyfile.call_count, 0)

    def test_ignore_remote_static(self, copyfile, *_):
        """Ensure ignoring of remote static video references."""
        self._run(CopyStatic, [get_video_ast("https://www.example.com/video.ogv")])
        self.assertEqual(copyfile.call_count, 0)

    def test_ignore_youtube(self, copyfile, *_):
        """Ensure ignoring of YouTube reference."""
        ast = [
            get_youtube_ast(
                "https://www.youtube.com/watch?v=C0DPdy98e4c",
                title="Test video",
            )
        ]
        self._run(CopyStatic, ast)
        self.assertEqual(copyfile.call_count, 0)

    def test_linked_picture(self, copyfile, *_):
        """Test a picture link."""
        ast = [
            get_generic_link_ast(
                [get_image_ast("/present.png")], "http://www.tu-berlin.de"
            )
        ]
        _, asts = self._run(CopyStatic, ast, languages=("en",))
        self.assertEqual(copyfile.call_count, 1)
        self.assertEqual(asts[0][0]["c"][1][0]["c"][2][0], "_en/present.png")

    def test_make_dst_dirs(self, *args):
        """Test creation of destination directories."""
        _, _, lexists, makedirs = args
        lexists.return_value = False
        ast = [get_image_ast("test.png")]
        self._run(CopyStatic, ast)
        self.assertEqual(makedirs.call_count, 8)
        for _, path in PATHS:
            with self.subTest(path):
                call_args = call(join(DEST, STATIC_FOLDER, "_en", *path))
                self.assertIn(call_args, makedirs.call_args_list)

    def test_only_en_present(self, copyfile, isfile, *_):
        """Test for when only en version present."""
        isfile.side_effect = _is_file_mock_only_en
        ast = [get_image_ast("localizable.gif")]
        languages = ("en", "la")
        _, asts = self._run(CopyStatic, ast, languages=languages)
        self.assertEqual(copyfile.call_count, 8)
        for i, (title, path) in enumerate(PATHS):
            with self.subTest(("en", title, path)):
                jpath = f"{'/'.join(path)}/" if path else ""
                call_args = call(
                    f"/source/en/_static/{jpath}localizable.gif",
                    f"/destination/_static/_en/{jpath}localizable.gif",
                )
                self.assertIn(call_args, copyfile.call_args_list)
                src = f"_en/{jpath}localizable.gif"
                self.assertEqual(asts[i][0]["c"][2][0], src)
        for i, (title, path) in enumerate(PATHS):
            with self.subTest(("la", title, path)):
                jpath = f"{'/'.join(path)}/" if path else ""
                call_args = call(
                    f"/source/_static/{jpath}localizable.gif",
                    f"/destination/_static/{jpath}localizable.gif",
                )
                self.assertIn(call_args, copyfile.call_args_list)
                idx = i + len(PATHS)
                src = f"{jpath}localizable.gif"
                self.assertEqual(asts[idx][0]["c"][2][0], src)

    def test_relative_localized(self, copyfile, *_):
        """Test a relative, localized reference."""
        ast = [get_video_ast("example_video.ogv")]
        _, asts = self._run(CopyStatic, ast, languages=("en",))
        self.assertEqual(copyfile.call_count, 4)
        for i, (title, path) in enumerate(PATHS):
            with self.subTest((title, path)):
                jpath = f"{'/'.join(path)}/" if path else ""
                call_args = call(
                    f"/source/en/_static/{jpath}example_video.ogv",
                    f"/destination/_static/_en/{jpath}example_video.ogv",
                )
                self.assertIn(call_args, copyfile.call_args_list)
                src = f"_en/{jpath}example_video.ogv"
                self.assertEqual(asts[i][0]["c"][2][0], src)

    def test_relative_nonlocalized(self, copyfile, isfile, *_):
        """Test a relative, non-localized reference."""
        isfile.side_effect = _is_file_mock_non_localized
        ast = [get_image_ast("example_image.jpg")]
        _, asts = self._run(CopyStatic, ast, languages=("en",))
        self.assertEqual(copyfile.call_count, 4)
        for i, (title, path) in enumerate(PATHS):
            with self.subTest((title, path)):
                jpath = f"{'/'.join(path)}/" if path else ""
                call_args = call(
                    f"/source/_static/{jpath}example_image.jpg",
                    f"/destination/_static/{jpath}example_image.jpg",
                )
                self.assertIn(call_args, copyfile.call_args_list)
                src = f"{jpath}example_image.jpg"
                self.assertEqual(asts[i][0]["c"][2][0], src)

    def test_relative_two_langs(self, copyfile, *_):
        """Test a relative reference for two languages."""
        languages = ("de", "en")
        ast = [get_image_ast("localized_present.png")]
        _, asts = self._run(CopyStatic, ast, languages=languages)
        self.assertEqual(copyfile.call_count, 8)
        for i, (title, path) in enumerate(PATHS):
            with self.subTest((title, path)):
                jpath = f"{'/'.join(path)}/" if path else ""
                call_args = call(
                    f"/source/de/_static/{jpath}localized_present.png",
                    f"/destination/_static/_de/{jpath}localized_present.png",
                )
                self.assertIn(call_args, copyfile.call_args_list)
                src = f"_de/{jpath}localized_present.png"
                self.assertEqual(asts[i][0]["c"][2][0], src)
        for i, (title, path) in enumerate(PATHS):
            with self.subTest((title, path)):
                jpath = f"{'/'.join(path)}/" if path else ""
                call_args = call(
                    f"/source/en/_static/{jpath}localized_present.png",
                    f"/destination/_static/_en/{jpath}localized_present.png",
                )
                self.assertIn(call_args, copyfile.call_args_list)
                src = f"_en/{jpath}localized_present.png"
                self.assertEqual(asts[i + len(PATHS)][0]["c"][2][0], src)

    def test_deep_single_picture(self, copyfile, *_):
        """Test a single, deeply-nested picture for two languages."""
        ast = [
            get_para_ast(),
            get_para_ast([get_image_ast("/present.png")]),
            get_para_ast([get_para_ast()]),
            get_para_ast([get_para_ast([get_para_ast()]), get_para_ast()]),
        ]
        _, asts = self._run(CopyStatic, ast)
        self.assertEqual(copyfile.call_count, 2)
        call_args = call(
            "/source/de/_static/present.png",
            "/destination/_static/_de/present.png",
        )
        self.assertIn(call_args, copyfile.call_args_list)
        call_args = call(
            "/source/en/_static/present.png",
            "/destination/_static/_en/present.png",
        )
        self.assertIn(call_args, copyfile.call_args_list)
        for i, (title, path) in enumerate(PATHS):
            with self.subTest((title, path)):
                self.assertEqual(asts[i][1]["c"][0]["c"][2][0], "_en/present.png")
        for i, (title, path) in enumerate(PATHS):
            with self.subTest((title, path)):
                self.assertEqual(
                    asts[i + len(PATHS)][1]["c"][0]["c"][2][0],
                    "_de/present.png",
                )
