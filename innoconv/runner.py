"""Runner module"""

import json
from os import makedirs, walk
from os.path import abspath, dirname, isdir, join, sep

from innoconv.constants import CONTENT_BASENAME
from innoconv.extensions import EXTENSIONS
from innoconv.utils import log, to_ast


class InnoconvRunner():
    """innoConv runner.

    Walks over the content directory tree and converts content files to JSON.
    Uses pandoc under the hood.
    """

    def __init__(self, source_dir, output_dir, manifest, extensions):
        self._source_dir = source_dir
        self._output_dir = output_dir
        self._manifest = manifest
        self._extensions = []
        self._load_extensions(extensions)
        self._toc = None

    def run(self):
        """Start the conversion.

        Iterate over language folders.
        """

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
                "Error: Directory {} does not exist".format(path))

        for root, dirs, files in walk(path):
            # note: all dirs manipulation must happen in-place!
            for i, directory in enumerate(dirs):
                if directory.startswith('_'):
                    del dirs[i]  # skip meta directories like '_static'
            dirs.sort()  # sort section names

            # process content file
            content_filename = '{}.md'.format(CONTENT_BASENAME)
            if content_filename in files:
                filepath = join(root, content_filename)
                self._process_file(filepath)
            else:
                raise RuntimeError(
                    "Found section without content file: {}".format(root))

    def _process_file(self, filepath):
        # relative path
        rel_path = dirname(filepath.replace(self._source_dir, '').lstrip(sep))
        # full filepath
        output_filename = '{}.json'.format(CONTENT_BASENAME)
        filepath_out = join(self._output_dir, rel_path, output_filename)

        self._notify_extensions('pre_process_file', rel_path)

        # convert file using pandoc
        ast, title = to_ast(filepath)

        self._notify_extensions('post_process_file', ast, title)

        # write file content
        makedirs(dirname(filepath_out), exist_ok=True)
        with open(filepath_out, 'w') as out_file:
            json.dump(ast, out_file)
        log("Wrote {}".format(filepath_out))

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
                    "Extension {} not found!".format(ext_name)) from exc
