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
from os.path import abspath, dirname, isdir, join, relpath

from innoconv.constants import CONTENT_BASENAME
from innoconv.ext import EXTENSIONS
from innoconv.utils import to_ast


class InnoconvRunner:
    """Convert content files in a directory tree."""

    def __init__(self, source_dir, output_dir, manifest, extensions):
        """Set defaults and load extensions."""
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
            raise RuntimeError(
                "Error: Directory {} does not exist".format(path)
            )

        section_num = 0
        for root, dirs, files in walk(path):
            # note: all dirs manipulation must happen in-place!
            for i, directory in enumerate(dirs):
                if directory.startswith("_"):
                    del dirs[i]  # skip meta directories like '_static'
            dirs.sort()  # sort section names

            # process content file
            content_filename = "{}.md".format(CONTENT_BASENAME)
            if content_filename in files:
                filepath = join(root, content_filename)
                self._process_file(filepath, lang_num, section_num)
                section_num += 1
            else:
                raise RuntimeError(
                    "Found section without content file: {}".format(root)
                )

        if section_num != len(self._sections):
            raise RuntimeError(
                "Inconsistent directory structure: "
                "Language {} is missing sections.".format(language)
            )

    def _process_file(self, filepath, lang_num, section_num):
        rel_path = dirname(relpath(filepath, self._source_dir))
        section_name = rel_path[3:]  # strip language
        if lang_num == 0:
            # record sections for first language
            self._sections.append(section_name)
        else:
            # ensure sections are identical for all languages
            try:
                if self._sections[section_num] != section_name:
                    raise RuntimeError(
                        "Inconsistent directory structure: "
                        "Section {} differs.".format(rel_path)
                    )
            except IndexError:
                raise RuntimeError(
                    "Inconsistent directory structure: "
                    "Extra section {} present.".format(rel_path)
                )

        # full filepath
        output_filename = "{}.json".format(CONTENT_BASENAME)
        filepath_out = join(self._output_dir, rel_path, output_filename)

        # convert file using pandoc
        self._notify_extensions("pre_process_file", rel_path)
        ast, title = to_ast(filepath)
        self._notify_extensions("post_process_file", ast, title)

        # write file content
        makedirs(dirname(filepath_out), exist_ok=True)
        with open(filepath_out, "w") as out_file:
            json.dump(ast, out_file)
        logging.info("Wrote %s", filepath_out)

        return title

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
                raise RuntimeError(
                    "Extension {} not found!".format(ext_name)
                ) from exc
        # pass extension list to extenions
        self._notify_extensions("extension_list", self._extensions)
