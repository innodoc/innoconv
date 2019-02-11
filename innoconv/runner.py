"""
The innoConv runner is the core of the conversion process.

It traverses the source directory recursively and finds all content files.
These are converted one-by-one to JSON. Under the hood is uses
`Pandoc <https://pandoc.org/>`_.

It receives a list of extensions that are instantiated and notified upon
certain events. The events are documented in
:class:`AbstractExtension <innoconv.extensions.abstract.AbstractExtension>`.
"""

import json
import logging
from os import makedirs, walk
from os.path import abspath, dirname, isdir, join, sep, isfile

from innoconv.constants import CONTENT_BASENAME, CUSTOM_CONTENT_FOLDER
from innoconv.extensions import EXTENSIONS
from innoconv.utils import to_ast


class InnoconvRunner():
    """Convert content files in a directory tree."""

    def __init__(self, source_dir, output_dir, manifest, extensions):
        self._source_dir = source_dir
        self._output_dir = output_dir
        self._manifest = manifest
        self._extensions = []
        self._load_extensions(extensions)
        self._toc = None

    def run(self):
        """Start the conversion by iterating over language folders."""

        self._notify_extensions('start', self._output_dir, self._source_dir)

        for language in self._manifest.languages:
            self._notify_extensions('pre_conversion', language)
            self._convert_language_folder(language)
            self._convert_custom_pages(language)
            self._notify_extensions('post_conversion', language)

        self._notify_extensions('finish')

    def _convert_custom_pages(self, language):
        if not hasattr(self._manifest, 'custom_content'):
            return

        path = abspath(join(self._source_dir, language, CUSTOM_CONTENT_FOLDER))

        for custom_content in self._manifest.custom_content:
            content_name = custom_content["name"]
            content_filename = f'{join(path, content_name)}.md'
            if isfile(content_filename):
                self._process_file(content_filename, content_name)
            else:
                raise RuntimeError(
                    f"Error: Missing {content_name} for language {language}")

    def _convert_language_folder(self, language):
        path = abspath(join(self._source_dir, language))

        if not isdir(path):
            raise RuntimeError(
                f"Error: Directory {path} does not exist")

        for root, dirs, files in walk(path):
            # note: all dirs manipulation must happen in-place!
            i = 0
            while i < len(dirs):
                if dirs[i].startswith('_'):
                    del dirs[i]  # skip meta directories like '_static'
                else:
                    i += 1
            dirs.sort()  # sort section names

            # process content file
            content_filename = '{}.md'.format(CONTENT_BASENAME)
            if content_filename in files:
                filepath = join(root, content_filename)
                self._process_file(filepath)
            else:
                raise RuntimeError(
                    f"Found section without content file: {root}")

    def _process_file(self, filepath, output_filename=None):
        # relative path
        rel_path = dirname(filepath.replace(self._source_dir, '').lstrip(sep))
        # full filepath
        if output_filename is None:
            output_filename = CONTENT_BASENAME
        output_filename = '{}.json'.format(output_filename)
        filepath_out = join(self._output_dir, rel_path, output_filename)

        # convert file using pandoc
        self._notify_extensions('pre_process_file', rel_path)
        ast, title = to_ast(filepath)
        self._notify_extensions('post_process_file', ast, title)

        # write file content
        makedirs(dirname(filepath_out), exist_ok=True)
        with open(filepath_out, 'w') as out_file:
            json.dump(ast, out_file)
        logging.info("Wrote %s", filepath_out)

        return title

    def _notify_extensions(self, event_name, *args, **kwargs):
        for ext in self._extensions:
            func = getattr(ext, event_name)
            func(*args, **kwargs)

    def _load_extensions(self, extensions):
        for ext_name in extensions:
            try:
                self._extensions.append(EXTENSIONS[ext_name](self._manifest))
            except (ImportError, KeyError) as exc:
                raise RuntimeError(
                    f"Extension {ext_name} not found!") from exc
