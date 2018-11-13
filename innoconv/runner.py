"""Runner module"""

from os import makedirs, walk
from os.path import abspath, dirname, isdir, join, sep, split

from innoconv.constants import (
    CONTENT_FILENAME, OUTPUT_CONTENT_FILENAME, MANIFEST_FILENAME, TOC_FILENAME)
from innoconv.utils import to_ast, set_debug, write_json_file


def splitall(path):
    """Split path into directory components."""
    all_parts = []
    while 1:
        parts = split(path)
        if parts[1] == path:
            all_parts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            all_parts.insert(0, parts[1])
    return all_parts


class InnoconvRunner():
    """innoConv runner.

    It walks over a directory tree and converts content files to JSON.
    """

    def __init__(self, source_dir, output_dir_base, languages, extensions,
                 debug=False):
        self.source_dir = source_dir
        self.output_dir_base = output_dir_base
        self.languages = languages
        self.extensions = extensions
        self._manifest = {}
        self._toc = None
        set_debug(debug)

    def run(self):
        """Start the conversion.

        Iterate over language folders.
        """

        self._notify_extensions('init', self.languages,
                                self.output_dir_base, self.source_dir)

        for language in self.languages:
            self._notify_extensions('pre_conversion', language)
            self._convert_language_folder(language)
            self._notify_extensions('post_conversion', language)

        self._notify_extensions('finish')

    def _convert_language_folder(self, language):
        """Convert a language folder.

        :param language: The language to convert and also the name of the
                         directory containing the content.
        :type language: Two character language code.
        """
        path = abspath(join(self.source_dir, language))

        if not isdir(path):
            raise RuntimeError(
                "Error: Directory {} does not exist".format(path))

        self._toc = []
        for root, dirs, files in walk(path):
            # note: all dirs manipulation must happen in-place!
            for i, directory in enumerate(dirs):
                if directory.startswith('_'):
                    del dirs[i]  # skip meta directories like '_static'
            dirs.sort()  # sort section names

            # process content file
            if CONTENT_FILENAME in files:
                filepath = join(root, CONTENT_FILENAME)
                self._process_file(filepath)
            else:
                raise RuntimeError(
                    "Found section without content file: {}".format(root))

        self._write_toc(language)
        self._write_manifest(language)

    def _write_toc(self, language):
        filepath = join(self.output_dir_base, language, TOC_FILENAME)
        write_json_file(
            filepath, self._toc, "Wrote TOC: {}".format(filepath))

    def _write_manifest(self, language):
        filepath = join(self.output_dir_base, language, MANIFEST_FILENAME)
        write_json_file(
            filepath, self._manifest, "Wrote manifest: {}".format(filepath))

    def _add_to_toc(self, dirpath, title):
        path_components = splitall(dirpath)
        path_components.pop(0)  # language
        if not path_components:
            # this is the root section
            self._manifest['title'] = title
            return
        children = self._toc
        while path_components:
            section_id = path_components.pop(0)
            # find/create child leaf
            found = None
            for child in children:
                if child['id'] == section_id:
                    found = child
                    try:
                        children = child['children']
                    except KeyError:
                        children = child['children'] = []
                        break
            # arrived at leaf -> add section
            if not found:
                children.append({
                    'id': section_id,
                    'title': title,
                })

    def _process_file(self, filepath):
        # input file relative path
        rel_path = dirname(filepath.replace(self.source_dir, '').lstrip(sep))
        # input file full path
        filepath_out = join(
            self.output_dir_base, rel_path, OUTPUT_CONTENT_FILENAME)

        self._notify_extensions('pre_process_file', rel_path)

        # convert file using pandoc
        ast, title = to_ast(filepath)

        self._notify_extensions('post_process_file', ast)

        # write file content
        makedirs(dirname(filepath_out), exist_ok=True)
        write_json_file(filepath_out, ast, "Wrote {}".format(filepath_out))

        self._add_to_toc(rel_path, title)

        return title

    def _notify_extensions(self, event_name, *args, **kwargs):
        for ext in self.extensions:
            func = getattr(ext, event_name)
            func(*args, **kwargs)
