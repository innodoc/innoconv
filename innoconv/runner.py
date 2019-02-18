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
from os.path import abspath, dirname, isdir, join, sep

from innoconv.constants import CONTENT_BASENAME
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
            self._notify_extensions('post_conversion', language)

        self._notify_extensions('finish')

    def _convert_language_folder(self, language):
        path = abspath(join(self._source_dir, language))

        if not isdir(path):
            raise RuntimeError(
                f"Error: Directory {path} does not exist")

        for root, dirs, files in walk(path):
            # note: all dirs manipulation must happen in-place!
            for i, directory in enumerate(dirs):
                if directory.startswith('_'):
                    del dirs[i]  # skip meta directories like '_static'
            dirs.sort()  # sort section names

            # process content file
            content_filename = f'{CONTENT_BASENAME}.md'
            if content_filename in files:
                filepath = join(root, content_filename)
                self._process_file(filepath)
            else:
                raise RuntimeError(
                    f"Found section without content file: {root}")

    def _process_file(self, filepath):
        # relative path
        rel_path = dirname(filepath.replace(self._source_dir, '').lstrip(sep))
        # full filepath
        output_filename = '{}.json'.format(CONTENT_BASENAME)
        filepath_out = join(self._output_dir, rel_path, output_filename)

        # convert file using pandoc
        self._notify_extensions('pre_process_file', rel_path)
        ast, title = to_ast(filepath)
        self._walk_ast(ast)
        self._notify_extensions('post_process_file', ast, title)

        # write file content
        makedirs(dirname(filepath_out), exist_ok=True)
        with open(filepath_out, 'w') as out_file:
            json.dump(ast, out_file)
        logging.info("Wrote %s", filepath_out)

        return title

    def _walk_ast(self, ast):
        def _process_ast_element(ast_element, parent_element=None):
            if isinstance(ast_element, list):
                _process_ast_array(ast_element, parent_element)
                return
            try:
                try:
                    ast_type = ast_element['t']
                except TypeError:
                    ast_type = None
                self._notify_extensions('process_ast_element', ast_element,
                                        ast_type, parent_element)

                for key in ast_element:
                    _process_ast_element(ast_element[key],
                                         parent_element=ast_element)
            except TypeError:
                pass

        def _process_ast_array(ast_array, parent_element=None):
            self._notify_extensions('process_ast_array',
                                    ast_array, parent_element)
            for ast_element in ast_array:
                _process_ast_element(ast_element, parent_element)

        _process_ast_element(ast)

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
