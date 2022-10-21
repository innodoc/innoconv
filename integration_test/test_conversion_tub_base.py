"""Integration tests for conversion process using entry-point innoconv."""

import json
from os import listdir, sep, walk
from os.path import isdir, isfile, join
from subprocess import PIPE, Popen

from innoconv.constants import (
    CONTENT_BASENAME,
    FOOTER_FRAGMENT_PREFIX,
    MANIFEST_BASENAME,
    PAGES_FOLDER,
    STATIC_FOLDER,
)
from innoconv.ext.tikz2svg import TIKZ_FOLDER
from . import BaseConversionTest, REPO_DIR

OUTPUT_CONTENT_FILENAME = f"{CONTENT_BASENAME}.json"


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
        with Popen(command, stdout=PIPE, stderr=PIPE) as process:
            stdout, stderr = process.communicate(timeout=60)
            stdout = stdout.decode("utf-8")
            stderr = stderr.decode("utf-8")
            if process.returncode != 0:
                print(stdout)
                print(stderr)
            self.assertEqual(process.returncode, 0)

        self._test_converted_folders_present()
        self._test_each_folder_has_content()
        self._test_footer_fragments()
        self._test_verbose_output(stderr)
        with self.subTest(extension="write_manifest"):
            manifest = self._test_write_manifest(stderr)
        self._test_pages(manifest)
        with self.subTest(extension="copystatic"):
            self._test_copy_static()
        with self.subTest(extension="join_strings"):
            self._test_join_strings()
        with self.subTest(extension="generate_toc"):
            self._test_generate_toc(manifest)
        with self.subTest(extension="tikz2svg"):
            self._test_tikz2svg()
        with self.subTest(extension="index_terms"):
            self._test_index_terms(manifest)
        with self.subTest(extension="number_cards"):
            self._test_number_cards(manifest)

    def _test_converted_folders_present(self):
        for lang in ("de", "en"):
            self.assertTrue(isdir(join(self.output_dir, lang)))
            self.assertTrue(isdir(join(self.output_dir, lang, "02-elements")))
            self.assertTrue(
                isdir(join(self.output_dir, lang, "02-elements", "02-headings"))
            )
            self.assertTrue(isdir(join(self.output_dir, lang, "01-project")))

    def _test_footer_fragments(self):
        for lang in ("de", "en"):
            for part in ("A", "B"):
                filename = f"{FOOTER_FRAGMENT_PREFIX}{part}.json"
                filepath = join(self.output_dir, lang, filename)
                with open(filepath, encoding="utf-8") as file:
                    data = json.load(file)
                    self.assertIsInstance(data, list)
                    self.assertTrue(len(data) > 1)

    def _test_each_folder_has_content(self):
        for lang in ("de", "en"):
            for dir_names, _, file_list in walk(join(self.output_dir, lang)):
                skip = False
                for dir_name in dir_names.split(sep):
                    if dir_name.startswith("_"):
                        skip = True
                if not skip:
                    self.assertIn(OUTPUT_CONTENT_FILENAME, file_list)

    def _test_pages(self, manifest):
        for lang in ("de", "en"):
            self.assertTrue(isdir(join(self.output_dir, lang, PAGES_FOLDER)))
            self.assertTrue(
                isfile(join(self.output_dir, lang, PAGES_FOLDER, "about.json"))
            )
            self.assertTrue(
                isfile(join(self.output_dir, lang, PAGES_FOLDER, "license.json"))
            )
        self.assertEqual(2, len(manifest["pages"]))
        page_about, page_license = manifest["pages"]

        self.assertEqual("about", page_about["id"])
        self.assertEqual("info-circle", page_about["icon"])
        self.assertEqual(True, page_about["link_in_nav"])
        self.assertEqual(True, page_about["link_in_footer"])
        self.assertEqual("Über diesen Kurs", page_about["title"]["de"])
        self.assertEqual("About this course", page_about["title"]["en"])
        self.assertEqual("Über", page_about["short_title"]["de"])
        self.assertEqual("About", page_about["short_title"]["en"])

        self.assertEqual("license", page_license["id"])
        self.assertEqual("copyright", page_license["icon"])
        self.assertEqual(False, page_license["link_in_nav"])
        self.assertEqual(True, page_license["link_in_footer"])
        self.assertEqual("Lizenz", page_license["title"]["de"])
        self.assertEqual("License", page_license["title"]["en"])
        self.assertEqual("Lizenz", page_license["short_title"]["de"])
        self.assertEqual("License", page_license["short_title"]["en"])

    def _test_join_strings(self):
        filepath = join(self.output_dir, "en", "01-project", OUTPUT_CONTENT_FILENAME)
        with open(filepath, encoding="utf-8") as file:
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
        for section in ("06-formulas", "10-interactive-exercises"):
            with self.subTest(section):
                path = join("de", "02-elements", section, "content.json")
                self.assertIn(path, stderr)
        self.assertIn("Build finished!", stderr)

    def _test_tikz2svg(self):
        folder = join(self.output_dir, STATIC_FOLDER, TIKZ_FOLDER)
        length = len([n for n in listdir(folder) if n.endswith(".svg")])
        self.assertEqual(length, 5)

    def _test_write_manifest(self, stderr):
        filepath = join(self.output_dir, f"{MANIFEST_BASENAME}.json")
        self.assertTrue(isfile(filepath))
        with open(filepath, encoding="utf-8") as file:
            data = json.load(file)
            self.assertIn("languages", data)
            self.assertIn("de", data["languages"])
            self.assertIn("en", data["languages"])
            self.assertIn("title", data)
            self.assertIn("de", data["title"])
            self.assertIn("en", data["title"])
            self.assertIn("mathjax", data)
            self.assertEqual("innoDoc", data["title"]["de"])
            self.assertEqual("innoDoc", data["title"]["en"])
            self.assertEqual("_logo.svg", data["logo"])
            self.assertEqual("/page/about", data["home_link"])
            self.assertEqual(90, data["min_score"])
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

    def _test_index_terms(self, manifest):
        self.assertIn("index_terms", manifest)
        index_terms = manifest["index_terms"]
        self.assertEqual(len(index_terms["de"]), len(index_terms["en"]))

        term, occurrences = index_terms["en"]["latex-formula"]
        self.assertEqual(term, "$\\LaTeX$ formula")
        self.assertEqual(1, len(occurrences))
        self.assertEqual("02-elements/11-index", occurrences[0][0])
        self.assertEqual("latex-formula-0", occurrences[0][1])

        term, occurrences = index_terms["de"]["latex-formel"]
        self.assertEqual(term, "$\\LaTeX$-Formel")
        self.assertEqual(1, len(occurrences))
        self.assertEqual("02-elements/11-index", occurrences[0][0])
        self.assertEqual("latex-formel-0", occurrences[0][1])

    def _test_number_cards(self, manifest):
        self.assertIn("cards", manifest)
        cards = manifest["cards"]
        self.assertEqual(
            list(cards.keys()),
            [
                "01-project/01-folders",
                "01-project/02-files/01-manifest",
                "01-project/02-files/02-content",
                "01-project/03-languages",
                "01-project/04-building",
                "02-elements/04-links/01-internal",
                "02-elements/04-links/02-external",
                "02-elements/06-formulas",
                "02-elements/07-media/01-pgf-tikz",
                "02-elements/10-interactive-exercises",
                "02-elements/10-interactive-exercises/01-text",
                "02-elements/10-interactive-exercises/02-checkbox",
                "02-elements/11-index",
            ],
        )

        self.assertEqual(
            cards["01-project/01-folders"],
            [
                ["example-1.1.1", "1.1.1", "example"],
                ["info-1.1.2", "1.1.2", "info"],
                ["info-1.1.3", "1.1.3", "info"],
            ],
        )
        self.assertEqual(
            cards["02-elements/10-interactive-exercises"],
            [
                ["EX_DUMMY", "2.10.1", "exercise", 0, 0],
                ["example-2.10.2", "2.10.2", "example"],
                ["EX_FULL", "2.10.3", "exercise", 4, 1],
            ],
        )
        self.assertEqual(
            cards["02-elements/11-index"],
            [
                ["example-2.11.1", "2.11.1", "example"],
                ["info-2.11.2", "2.11.2", "info"],
            ],
        )
