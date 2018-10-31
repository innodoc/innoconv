"""Runner module"""

from os import makedirs, walk
from os.path import abspath, dirname, isdir, join, sep, isfile

from innoconv.constants import (
    CONTENT_FILENAME, OUTPUT_CONTENT_FILENAME, DEFAULT_LANGUAGES)
from innoconv.utils import to_ast, log, set_debug, write_json_file

from innoconv.modloader import run_mods


class InnoconvRunner():
    """innoConv runner.

    It walks over a directory tree and converts content files to JSON.
    """

    def __init__(self, source_dir,
                 output_dir_base,
                 modules, debug=False, languages=None):
        self.source_dir = source_dir
        self.output_dir_base = output_dir_base
        if languages is None:
            self.languages = DEFAULT_LANGUAGES[:]
        else:
            self.languages = languages

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

            if CONTENT_FILENAME in files and not veto:

                filepath = join(root, CONTENT_FILENAME)
                self._process_file(filepath)
            # else:
            #    raise RuntimeError(
            #        "Found section without content file: {}".format(root))
            # commented out because this is necessary for copystatic

        run_mods(self.modules, 'post_language')

    def _process_file(self, filepath):

        if isfile(filepath):
            rel_path = dirname(
                filepath.replace(self.source_dir, '').lstrip(sep))
            run_mods(self.modules, 'pre_content_file',
                     rel_path=rel_path,
                     full_path=filepath)

            ast = to_ast(filepath)

            run_mods(self.modules, 'process_ast',
                     ast=ast)

            ast = ast['blocks']

            filepath_out = join(
                self.output_dir_base, rel_path, OUTPUT_CONTENT_FILENAME)
            makedirs(dirname(filepath_out), exist_ok=True)

            write_json_file(
                filepath_out, ast, "Wrote {}".format(filepath_out))

            run_mods(self.modules, 'post_content_file')
            log('Wrote {}'.format(filepath_out))
