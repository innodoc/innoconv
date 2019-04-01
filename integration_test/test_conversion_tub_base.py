"""Integration tests for conversion process using entry-point innoconv."""

import json
from os import remove, sep, walk
from os.path import dirname, isdir, isfile, join, realpath
from subprocess import PIPE, Popen
from tempfile import TemporaryDirectory
import unittest

from innoconv.constants import CONTENT_BASENAME, STATIC_FOLDER

REPO_DIR = join(dirname(realpath(__file__)), "tub_base")
EXTRA_FILE = join(REPO_DIR, "de", STATIC_FOLDER, "TESTFILE.txt")
OUTPUT_CONTENT_FILENAME = "{}.json".format(CONTENT_BASENAME)


class TestConversionTubBase(unittest.TestCase):
    """Test conversion of tub_base course."""

    def setUp(self):
        """Prepare temp dirs and create extra file."""
        self.tmp_dir = TemporaryDirectory(prefix="innoconv-test-output-")
        self.output_dir = self.tmp_dir.name
        with open(EXTRA_FILE, "w+") as file:
            file.write("lorem Ipsum")

    def tearDown(self):
        """Clean up temp dirs and extra file."""
        self.tmp_dir.cleanup()
        remove(EXTRA_FILE)

    def test_conversion(self):
        """A conversion should run without problems."""
        command = [
            "innoconv",
            "--force",  # TODO: why do tests fail without this???
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
        with self.subTest(extension="copystatic"):
            self._test_copy_static(stderr)
        with self.subTest(extension="generate_toc"):
            self._test_generate_toc(stderr)
        with self.subTest(extension="join_strings"):
            self._test_content()
        with self.subTest(extension="tikz2svg"):
            self._test_tikz2svg(stderr)
        with self.subTest(extension="write_manifest"):
            self._test_write_manifest(stderr)

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

    def _test_content(self):
        filepath = join(self.output_dir, "de", OUTPUT_CONTENT_FILENAME)
        with open(filepath) as file:
            data = json.load(file)
            paragraph = data[0]
            self.assertEqual(paragraph["t"], "Para")
            content = paragraph["c"][0]
            self.assertEqual(content["t"], "Str")
            self.assertIn("Dies ist ein Beispiel-Kurs", content["c"])

    def _test_copy_static(self, stderr):
        self.assertTrue(isdir(join(self.output_dir, STATIC_FOLDER)))
        self.assertTrue(isdir(join(self.output_dir, STATIC_FOLDER, "_de")))
        self.assertTrue(
            isfile(join(self.output_dir, STATIC_FOLDER, "adam.jpg"))
        )
        self.assertTrue(
            isfile(join(self.output_dir, STATIC_FOLDER, "_de", "flag.png"))
        )
        self.assertTrue(
            isfile(
                join(
                    self.output_dir,
                    STATIC_FOLDER,
                    "_de",
                    "02-elements",
                    "06-media",
                    "TU_Logo.png",
                )
            )
        )
        self.assertFalse(
            isfile(join(self.output_dir, STATIC_FOLDER, "flag.png"))
        )
        self.assertFalse(
            isfile(join(self.output_dir, STATIC_FOLDER, "_de", "TESTFILE.txt"))
        )
        self.assertIn("8 files found", stderr)
        self.assertIn(
            join(
                self.output_dir,
                STATIC_FOLDER,
                "_de",
                "02-elements",
                "06-media",
                "TU_Logo.png",
            ),
            stderr,
        )

    def _test_verbose_output(self, stderr):
        for section in ("03-links-and-formatting", "04-quotes"):
            with self.subTest(section):
                path = join("de", "02-elements", section, "content.json")
                self.assertIn(path, stderr)
        self.assertIn("Build finished!", stderr)

    @unittest.skip("TODO")
    def _test_tikz2svg(self, stderr):
        # test content in tub_base has to be prepared
        pass

    @unittest.skip("TODO")
    def _test_generate_toc(self, stderr):
        pass

    @unittest.skip("TODO")
    def _test_write_manifest(self, stderr):
        pass
