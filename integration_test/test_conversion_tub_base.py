"""Integration tests for conversion process using entry-point innoconv."""

import json
from os import listdir, sep, walk
from os.path import basename, isdir, isfile, join
from subprocess import PIPE, Popen

from innoconv.constants import (
    CONTENT_BASENAME,
    MANIFEST_BASENAME,
    PAGES_FOLDER,
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

    def setUp(self):
        """Init attributes."""
        super().setUp()
        self._section_output_dirs = {}

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
        self.assertIs(process.returncode, 0)

        for lang in ("de", "en"):
            self._section_output_dirs[lang] = [
                join(self.output_dir, dirname.replace(REPO_DIR + sep, ""))
                for dirname, *_ in walk(join(REPO_DIR, lang))
                if not basename(dirname).startswith("_")
                and STATIC_FOLDER not in dirname
            ]

        self._test_section_folders_present()
        self._test_each_folder_has_content()
        self._test_verbose_output(stderr)
        manifest = self._test_write_manifest()
        self._test_pages_present(manifest["pages"])
        self._test_fragments_present()
        self._test_copy_static()
        self._test_generate_toc(manifest["toc"])
        self._test_index_terms(manifest["index_terms"])
        self._test_join_strings()
        self._test_tikz2svg()

    def _test_section_folders_present(self):
        for lang in ("de", "en"):
            for dir_name in self._section_output_dirs[lang]:
                with self.subTest(dir_name=dir_name):
                    self.assertTrue(isdir(dir_name))

    def _test_each_folder_has_content(self):
        for lang in ("de", "en"):
            for dir_name in self._section_output_dirs[lang]:
                with self.subTest(dir_name=dir_name):
                    self.assertIn(OUTPUT_CONTENT_FILENAME, listdir(dir_name))

    def _test_pages_present(self, pages):
        self.assertIs(len(pages), 2)
        about_page, license_page = pages
        self.assertEqual(about_page["id"], "about")
        self.assertEqual(about_page["icon"], "info-circle")
        self.assertEqual(about_page["link_in_nav"], True)
        self.assertEqual(about_page["link_in_footer"], True)
        self.assertEqual(license_page["id"], "license")
        self.assertEqual(license_page["icon"], "copyright")
        self.assertEqual(license_page["link_in_nav"], False)
        self.assertEqual(license_page["link_in_footer"], True)
        for lang in ("de", "en"):
            for page in ("about", "license"):
                file = join(
                    self.output_dir, lang, PAGES_FOLDER, "{}.json".format(page)
                )
                with self.subTest(file=file):
                    self.assertTrue(isfile(file))

    def _test_fragments_present(self):
        for lang in ("de", "en"):
            for part in ("a", "b"):
                file = join(
                    self.output_dir, lang, "_footer_{}.json".format(part)
                )
                with self.subTest(file=file):
                    self.assertTrue(isfile(file))

    def _test_verbose_output(self, stderr):
        for lang in ("de", "en"):
            for dir_name in self._section_output_dirs[lang]:
                with self.subTest(dir_name=dir_name):
                    self.assertIn(dir_name, stderr)
        self.assertIn("Wrote manifest", stderr)

    def _test_copy_static(self):
        # files in <root>/<STATIC_FOLDER>
        static_files = [
            [
                join(self.output_dir, dirname.replace(REPO_DIR + sep, ""), file)
                for file in files
            ]
            for dirname, _, files in walk(join(REPO_DIR, STATIC_FOLDER))
        ]
        # files in <root>/<lang>/<STATIC_FOLDER>
        for lang in ("de", "en"):
            static_files += [
                [
                    join(
                        self.output_dir,
                        dirname.replace(REPO_DIR + sep, ""),
                        file,
                    ).replace(
                        # <lang>/<STATIC_FOLDER>/file
                        # -> <STATIC_FOLDER>/_<lang>/file
                        join(lang, STATIC_FOLDER),
                        join(STATIC_FOLDER, "_{}".format(lang)),
                    )
                    for file in files
                ]
                for dirname, _, files in walk(
                    join(REPO_DIR, lang, STATIC_FOLDER)
                )
            ]
        # remove dups
        static_files = list(
            dict.fromkeys(
                # flatten list
                [file for sublist in static_files for file in sublist]
            )
        )

        for file in static_files:
            with self.subTest(file=file):
                self.assertTrue(isfile(file))

    def _test_generate_toc(self, toc):
        def _test_section(path, parent, children, toc_entry=None):
            section_id = path.replace(parent + sep, "")
            if toc_entry:
                self.assertEqual(toc_entry["id"], section_id)
                self.assertIn("de", toc_entry["title"])
                self.assertIn("en", toc_entry["title"])
            subdirs = [
                d
                for d in listdir(path)
                if isdir(join(path, d)) and not d.startswith("_")
            ]
            if subdirs:
                for index, dir_name in enumerate(sorted(subdirs)):
                    subsection = children[index]
                    subsection_children = (
                        subsection["children"]
                        if "children" in subsection
                        else None
                    )
                    _test_section(
                        join(path, dir_name),
                        path,
                        subsection_children,
                        subsection,
                    )
            else:
                self.assertIsNone(children)

        _test_section(join(REPO_DIR, "en"), REPO_DIR, toc)

    def _test_index_terms(self, index_terms):
        # TODO
        pass

    def _test_join_strings(self):
        exp_de = (
            "Ein Kurs besteht aus einer Anzahl von Kapiteln, Abschnitten"
            " und Unterabschnitten."
        )
        exp_en = (
            "A course consists of a number of chapters, sections"
            " and subsections."
        )
        for lang, exp in (("de", exp_de), ("en", exp_en)):
            filepath = join(
                self.output_dir, lang, "01-project", OUTPUT_CONTENT_FILENAME
            )
            with open(filepath) as file:
                data = json.load(file)
                paragraph = data[0]
                content = paragraph["c"][0]
                with self.subTest(file=file):
                    self.assertEqual(content["t"], "Str")
                    self.assertIn(exp, content["c"])

    def _test_tikz2svg(self):
        folder = join(self.output_dir, STATIC_FOLDER, TIKZ_FOLDER)
        length = len([n for n in listdir(folder) if n.endswith(".svg")])
        self.assertIs(length, 5)

    def _test_write_manifest(self):
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
        self.assertIn("logo", data)
        self.assertIn("home_link", data)
        self.assertEqual("innoDoc", data["title"]["de"])
        self.assertEqual("innoDoc", data["title"]["en"])
        return data
