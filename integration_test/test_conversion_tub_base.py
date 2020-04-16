"""Integration tests for conversion process using entry-point innoconv."""

import json
from os import listdir, sep, walk
from os.path import isdir, isfile, join
from subprocess import PIPE, Popen

from innoconv.constants import (
    CONTENT_BASENAME,
    MANIFEST_BASENAME,
    STATIC_FOLDER,
)
from innoconv.ext.tikz2svg import TIKZ_FOLDER
from . import BaseConversionTest, REPO_DIR

OUTPUT_CONTENT_FILENAME = "{}.json".format(CONTENT_BASENAME)


class TestConversionTubBase(BaseConversionTest):
    """
    Test conversion of tub_base course.

    Extensive test of innoConv features combined including extensions.
    """

    def test_conversion(self):
        """A conversion should run without problems."""
        command = [
            "innoconv",
            "--verbose",
            "--output-dir",
            self.output_dir,
            REPO_DIR,
        ]
        process = Popen(command, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate(timeout=60)
        stdout = stdout.decode("utf-8")
        stderr = stderr.decode("utf-8")
        if process.returncode != 0:
            print(stdout)
            print(stderr)
        self.assertEqual(process.returncode, 0)
        self._test_converted_folders_present()
        self._test_each_folder_has_content()
        self._test_verbose_output(stderr)
        with self.subTest(extension="write_manifest"):
            manifest_data = self._test_write_manifest(stderr)
        self._test_pages(manifest_data)
        with self.subTest(extension="copystatic"):
            self._test_copy_static()
        with self.subTest(extension="join_strings"):
            self._test_join_strings()
        with self.subTest(extension="generate_toc"):
            self._test_generate_toc(manifest_data)
        with self.subTest(extension="tikz2svg"):
            self._test_tikz2svg()
        with self.subTest(extension="index_terms"):
            self._test_index_terms(manifest_data)

    def _test_converted_folders_present(self):
        for lang in ("de", "en"):
            self.assertTrue(isdir(join(self.output_dir, lang)))
            self.assertTrue(isdir(join(self.output_dir, lang, "02-elements")))
            self.assertTrue(
                isdir(join(self.output_dir, lang, "02-elements", "02-headings"))
            )
            self.assertTrue(isdir(join(self.output_dir, lang, "01-project")))

    def _test_each_folder_has_content(self):
        for lang in ("de", "en"):
            for dir_names, _, file_list in walk(join(self.output_dir, lang)):
                skip = False
                for dir_name in dir_names.split(sep):
                    if dir_name.startswith("_"):
                        skip = True
                if not skip:
                    self.assertIn(OUTPUT_CONTENT_FILENAME, file_list)

    def _test_pages(self, data):
        # TODO
        for lang in ("de", "en"):
            pass

    def _test_join_strings(self):
        filepath = join(self.output_dir, "en", "01-project", OUTPUT_CONTENT_FILENAME)
        with open(filepath) as file:
            data = json.load(file)
            paragraph = data[0]
            self.assertEqual(paragraph["t"], "Para")
            content = paragraph["c"][0]
            self.assertEqual(content["t"], "Str")
            self.assertIn(
                "A course consists of a number of chapters, sections and subsections.",
                content["c"],
            )

    def _test_copy_static(self):
        files = (
            ("02-elements", "07-media", "adam.jpg"),
            ("02-elements", "07-media", "star.png"),
            ("02-elements", "07-media", "tu-logo.png"),
            ("02-elements", "07-media", "video.mp4"),
            ("subfolder", "math.jpg"),
            ("_en", "02-elements", "07-media", "lines.png"),
            ("_de", "02-elements", "07-media", "lines.png"),
        )
        for file in files:
            with self.subTest(file=file):
                full_filename = join(self.output_dir, STATIC_FOLDER, *file)
                self.assertTrue(isfile(full_filename))

    def _test_verbose_output(self, stderr):
        for section in ("06-formulas", "09-interactive-exercises"):
            with self.subTest(section):
                path = join("de", "02-elements", section, "content.json")
                self.assertIn(path, stderr)
        self.assertIn("Build finished!", stderr)

    def _test_tikz2svg(self):
        folder = join(self.output_dir, STATIC_FOLDER, TIKZ_FOLDER)
        length = len([n for n in listdir(folder) if n.endswith(".svg")])
        self.assertEqual(length, 5)

    def _test_write_manifest(self, stderr):
        filepath = join(self.output_dir, "{}.json".format(MANIFEST_BASENAME))
        self.assertTrue(isfile(filepath))
        with open(filepath) as file:
            data = json.load(file)
            self.assertIn("languages", data)
            self.assertIn("de", data["languages"])
            self.assertIn("en", data["languages"])
            self.assertIn("title", data)
            self.assertIn("de", data["title"])
            self.assertIn("en", data["title"])
            self.assertEqual("innoDoc", data["title"]["de"])
            self.assertEqual("innoDoc", data["title"]["en"])
            self.assertEqual("_logo.svg", data["logo"])
            self.assertEqual("/page/about", data["home_link"])
            self.assertEqual(2, len(data["pages"]))
        self.assertIn("Wrote manifest", stderr)
        return data

    def _test_generate_toc(self, data):
        self.assertIn("toc", data)
        sec_proj = data["toc"][0]
        self.assertEqual("Projektstruktur", sec_proj["title"]["de"])
        self.assertEqual("Project structure", sec_proj["title"]["en"])
        self.assertEqual("01-project", sec_proj["id"])
        self.assertEqual(4, len(sec_proj["children"]))
        sec_folders = sec_proj["children"][0]
        self.assertEqual("Ordnerstruktur", sec_folders["title"]["de"])
        self.assertEqual("Folders", sec_folders["title"]["en"])
        self.assertEqual("01-folders", sec_folders["id"])
        self.assertNotIn("children", sec_folders)

    def _test_index_terms(self, data):
        # TODO
        pass
