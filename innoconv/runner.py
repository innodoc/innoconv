"""
The innoConv runner is the core of the conversion process.

It traverses the source directory recursively and finds all content files.
These are converted one-by-one to JSON. Under the hood is uses
`Pandoc <https://pandoc.org/>`_.

It receives a list of extensions that are instantiated and notified upon
certain events. The events are documented in
:class:`AbstractExtension <innoconv.ext.abstract.AbstractExtension>`.
"""

import json
import logging
from os import makedirs, walk
from os.path import abspath, dirname, exists, isdir, join, relpath
import pathlib

from innoconv.constants import (
    CONTENT_BASENAME,
    FOOTER_FRAGMENT_PREFIX,
    PAGES_FOLDER,
)
from innoconv.ext import EXTENSIONS
from innoconv.utils import to_ast


class InnoconvRunner:
    """
    Convert content files in a directory tree.

    :param source_dir: Content source directory.
    :type source_dir: str

    :param output_dir: Output directory.
    :type output_dir: str

    :param manifest: Content manifest.
    :type manifest: innoconv.manifest.Manifest

    :param extensions: List of extension names to use.
    :type extensions: list[str]
    """

    def __init__(self, source_dir, output_dir, manifest, extensions):
        """Initialize InnoconvRunner."""
        self._source_dir = source_dir
        self._output_dir = output_dir
        self._manifest = manifest
        self._extensions = []
        self._load_extensions(extensions)
        self._sections = []

    def run(self):
        """Start the conversion by iterating over language folders."""
        self._notify_extensions("start", self._output_dir, self._source_dir)

        for i, language in enumerate(self._manifest.languages):
            self._notify_extensions("pre_conversion", language)
            self._convert_language_folder(language, i)
            self._notify_extensions("post_conversion", language)

        self._notify_extensions("finish")

    def _convert_language_folder(self, language, lang_num):
        path = abspath(join(self._source_dir, language))

        if not isdir(path):
            raise RuntimeError(f"Error: Directory {path} does not exist")

        section_num = 0
        for root, dirs, files in walk(path):
            rel_path = relpath(root, path)

            # skip meta directories like '_static'
            parts = pathlib.Path(rel_path).parts
            if parts and parts[0].startswith("_"):
                continue

            # note: all dirs manipulation must happen in-place!
            dirs.sort()  # sort section names

            # process section
            content_filename = f"{CONTENT_BASENAME}.md"
            if content_filename in files:
                filepath = join(root, content_filename)
                self._process_section(filepath, lang_num, section_num)
                section_num += 1
            else:
                raise RuntimeError(f"Found section without content file: {root}")

        if section_num != len(self._sections):
            msg = (
                "Inconsistent directory structure: "
                f"Language {language} is missing sections."
            )
            raise RuntimeError(msg)

        # process pages
        try:
            pages = self._manifest.pages
        except AttributeError:
            pages = []
        for page in pages:
            self._process_page(page, language)

        # process footer fragments
        self._process_footer_fragments(language)

    def _process_section(self, filepath, lang_num, section_num):
        rel_path = dirname(relpath(filepath, self._source_dir))
        section_name = rel_path[3:]  # strip language
        if lang_num == 0:
            # record sections for first language
            self._sections.append(section_name)
        else:
            # ensure sections are identical for all languages
            try:
                if self._sections[section_num] != section_name:
                    msg = (
                        "Inconsistent directory structure: "
                        f"Section {rel_path} differs."
                    )
                    raise RuntimeError(msg)
            except IndexError as err:
                msg = (
                    "Inconsistent directory structure: "
                    f"Extra section {rel_path} present."
                )
                raise RuntimeError(msg) from err

        # full filepath
        output_filename = f"{CONTENT_BASENAME}.json"
        filepath_out = join(self._output_dir, rel_path, output_filename)

        # convert file using pandoc
        self._notify_extensions("pre_process_file", rel_path)
        ast, title, short_title, section_type = to_ast(filepath)
        self._notify_extensions(
            "post_process_file", ast, title, "section", section_type, short_title
        )

        # write file content
        makedirs(dirname(filepath_out), exist_ok=True)
        with open(filepath_out, "w") as out_file:
            json.dump(ast, out_file)
        logging.info("Wrote %s", filepath_out)

        return title

    def _process_page(self, page, language):
        try:
            link_in_nav = page["link_in_nav"]
        except KeyError:
            link_in_nav = False
        try:
            link_in_footer = page["link_in_footer"]
        except KeyError:
            link_in_footer = False
        if not (link_in_nav or link_in_footer):
            logging.warning(
                "Page '%s' should have at least on of "
                "link_in_nav or link_in_nav set to true."
            )
            return
        try:
            page["title"]
        except KeyError:
            page["title"] = {}
        input_filename = f"{page['id']}.md"
        filepath = join(self._source_dir, language, PAGES_FOLDER, input_filename)
        rel_path = dirname(relpath(filepath, self._source_dir))

        # convert
        self._notify_extensions("pre_process_file", rel_path)
        ast, title, short_title, _ = to_ast(filepath)
        self._notify_extensions("post_process_file", ast, title, "page", None)
        try:
            page["short_title"][language] = short_title
        except KeyError:
            page["short_title"] = {language: short_title}
        page["title"][language] = title

        # write json output
        output_filename = f"{page['id']}.json"
        filepath_out = join(self._output_dir, rel_path, output_filename)
        makedirs(dirname(filepath_out), exist_ok=True)
        with open(filepath_out, "w") as out_file:
            json.dump(ast, out_file)
        logging.info("Wrote %s", filepath_out)

    def _process_footer_fragments(self, language):
        for part in ("a", "b"):
            input_filename = f"{FOOTER_FRAGMENT_PREFIX}{part}.md"
            filepath = join(self._source_dir, language, input_filename)
            rel_path = dirname(relpath(filepath, self._source_dir))
            if not exists(filepath):
                logging.warning("Footer fragment %s does not exist.", filepath)
                continue

            # convert
            self._notify_extensions("pre_process_file", rel_path)
            ast, title, _, _ = to_ast(filepath, ignore_missing_title=True)
            self._notify_extensions("post_process_file", ast, title, "fragment", None)

            # write json output
            output_filename = f"{FOOTER_FRAGMENT_PREFIX}{part}.json"
            filepath_out = join(self._output_dir, rel_path, output_filename)
            makedirs(dirname(filepath_out), exist_ok=True)
            with open(filepath_out, "w") as out_file:
                json.dump(ast, out_file)
            logging.info("Wrote %s", filepath_out)

    def _notify_extensions(self, event_name, *args, **kwargs):
        for ext in self._extensions:
            func = getattr(ext, event_name)
            func(*args, **kwargs)

    def _load_extensions(self, extensions):
        # load extensions
        for ext_name in extensions:
            try:
                self._extensions.append(EXTENSIONS[ext_name](self._manifest))
            except (ImportError, KeyError) as exc:
                raise RuntimeError(f"Extension {ext_name} not found!") from exc
        # pass extension list to extenions
        self._notify_extensions("extension_list", self._extensions)
