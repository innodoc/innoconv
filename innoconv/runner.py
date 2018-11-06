"""Runner module"""

from os import makedirs, walk
from os.path import abspath, dirname, isdir, join, sep, split

from innoconv.constants import (
    CONTENT_FILENAME, OUTPUT_CONTENT_FILENAME, MANIFEST_FILENAME, TOC_FILENAME)
from innoconv.utils import to_ast, set_debug, write_json_file

from innoconv.modloader import run_mods


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

    def __init__(self, source_dir,
                 output_dir_base, languages,
                 modules, debug=False):
        self.source_dir = source_dir
        self.output_dir_base = output_dir_base
        self.languages = languages
        self._manifest = {}
        self._toc = None

        self.debug = debug
        self.modules = modules

        set_debug(debug)

    def run(self):
        """Start the conversion.

        Iterate over language folders.
        """

        run_mods(self.modules, 'load_languages',
                 languages=self.languages
                 )

        run_mods(self.modules, 'pre_conversion',
                 base_dirs={
                     "output": self.output_dir_base,
                     "source": self.source_dir
                 })

        for language in self.languages:
            self._convert_folder(language)

        run_mods(self.modules, 'post_conversion')

    def _convert_folder(self, language):
        """Convert a language folder."""
        path = abspath(join(self.source_dir, language))

        run_mods(self.modules, 'pre_language',
                 language=language)

        if not isdir(path):
            raise RuntimeError(
                "Error: Directory {} does not exist".format(path))

        self._toc = []
        for root, dirs, files in walk(path):

            rel_dir = root[len(self.source_dir):].lstrip(sep)

            # note: all dirs manipulation must happen in-place!
            for i, directory in enumerate(dirs):
                if directory.startswith('_'):
                    del dirs[i]  # skip meta directories like '_static'
            dirs.sort()  # sort section names

            veto = run_mods(self.modules, 'pre_processing_veto',
                            dir=rel_dir,
                            filename=CONTENT_FILENAME)

            # process content file
            if CONTENT_FILENAME in files and not veto:
                filepath = join(root, CONTENT_FILENAME)
                self._process_file(filepath)
            else:
                raise RuntimeError(
                    "Found section without content file: {}".format(root))

        self._write_toc(language)
        self._write_manifest(language)

        run_mods(self.modules, 'post_language')

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

        # save content file
        rel_path = dirname(filepath.replace(self.source_dir, '').lstrip(sep))

        run_mods(self.modules, 'pre_content_file',
                 rel_path=rel_path,
                 full_path=filepath)

        ast, title = to_ast(filepath)

        run_mods(self.modules, 'process_ast',
                 ast=ast)

        filepath_out = join(
            self.output_dir_base, rel_path, OUTPUT_CONTENT_FILENAME)
        makedirs(dirname(filepath_out), exist_ok=True)
        write_json_file(
            filepath_out, ast, "Wrote {}".format(filepath_out))

        # add to TOC
        self._add_to_toc(rel_path, title)

        run_mods(self.modules, 'post_content_file')

        return title
