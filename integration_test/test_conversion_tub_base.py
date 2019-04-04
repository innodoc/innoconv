"""Integration tests for conversion process using entry-point innoconv."""

import json
from os import listdir, sep, walk
from os.path import dirname, isdir, isfile, join, realpath
from subprocess import PIPE, Popen
from tempfile import TemporaryDirectory
import unittest

from innoconv.constants import (
    CONTENT_BASENAME,
    MANIFEST_BASENAME,
    STATIC_FOLDER,
)
from innoconv.ext.tikz2svg import TIKZ_FOLDER

REPO_DIR = join(dirname(realpath(__file__)), "tub_base")
OUTPUT_CONTENT_FILENAME = "{}.json".format(CONTENT_BASENAME)


class TestConversionTubBase(unittest.TestCase):
    """Test conversion of tub_base course."""

    def setUp(self):
        """Prepare temp dirs and create extra file."""
        self.tmp_dir = TemporaryDirectory(prefix="innoconv-test-output-")
        self.output_dir = join(self.tmp_dir.name, "innoconv_output")

    def tearDown(self):
        """Clean up temp dirs and extra file."""
        self.tmp_dir.cleanup()

    def test_conversion(self):
        """A conversion should run without problems."""
        command = [
            "innoconv",
            "--verbose",
            "--output-dir",
            self.output_dir,
            "--extensions",
            "join_strings,copy_static,generate_toc,tikz2svg,write_manifest",
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
        with self.subTest(extension="copystatic"):
            self._test_copy_static()
        with self.subTest(extension="join_strings"):
            self._test_join_strings()
        with self.subTest(extension="write_manifest"):
            data = self._test_write_manifest(stderr)
        with self.subTest(extension="generate_toc"):
            self._test_generate_toc(data)
        with self.subTest(extension="tikz2svg"):
            self._test_tikz2svg()

    def _test_converted_folders_present(self):
        for lang in ("de", "en"):
            self.assertTrue(isdir(join(self.output_dir, lang)))
            self.assertTrue(isdir(join(self.output_dir, lang, "02-elements")))
            self.assertTrue(
                isdir(join(self.output_dir, lang, "02-elements", "01-headers"))
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

    def _test_join_strings(self):
        filepath = join(self.output_dir, "de", OUTPUT_CONTENT_FILENAME)
        with open(filepath) as file:
            data = json.load(file)
            paragraph = data[0]
            self.assertEqual(paragraph["t"], "Para")
            content = paragraph["c"][0]
            self.assertEqual(content["t"], "Str")
            self.assertIn("Dies ist ein Beispiel-Kurs", content["c"])

    def _test_copy_static(self):
        files = (
            ("02-elements", "06-media", "adam.jpg"),
            ("02-elements", "06-media", "star.png"),
            ("02-elements", "06-media", "tu-logo.png"),
            ("02-elements", "06-media", "video.mp4"),
            ("subfolder", "math.jpg"),
            ("_en", "02-elements", "06-media", "lines.png"),
            ("_de", "02-elements", "06-media", "lines.png"),
        )
        for file in files:
            with self.subTest(file=file):
                full_filename = join(self.output_dir, STATIC_FOLDER, *file)
                self.assertTrue(isfile(full_filename))

    def _test_verbose_output(self, stderr):
        for section in ("03-links-and-formatting", "04-quotes"):
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
            self.assertEqual("innoDoc-Showcase-Kurs", data["title"]["de"])
            self.assertEqual("innoDoc Showcase Course", data["title"]["en"])
        self.assertIn("Wrote manifest", stderr)
        return data

    def _test_generate_toc(self, data):
        self.assertIn("toc", data)
        self.assertIn("title", data["toc"][0])
        self.assertIn("id", data["toc"][0])
        self.assertIn("children", data["toc"][0])
        self.assertEqual(4, len(data["toc"][0]["children"]))
        self.assertEqual("01-project", data["toc"][0]["id"])
        self.assertIn("de", data["toc"][0]["title"])
        self.assertIn("en", data["toc"][0]["title"])
        self.assertEqual("Projektstruktur", data["toc"][0]["title"]["de"])
        self.assertEqual("Project structure", data["toc"][0]["title"]["en"])
