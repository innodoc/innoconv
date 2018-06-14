"""Runner module"""

import json
import os

from innoconv.utils import to_ast, log


# TODO: write toc.json

# TODO: create post-process module system
#        - copy static files
#        - concatenate Str and Space

class InnoconvRunner():
    """innoConv runner.

    It walks over the course files and converts them to JSON.
    """

    def __init__(self, source_dir, output_dir_base, languages, debug=False):
        self.source_dir = source_dir
        self.output_dir_base = output_dir_base
        self.languages = languages
        self.debug = debug

    def run(self):
        """Start the conversion.

        Iterates over the language folders.
        """
        for language in self.languages:
            self._convert_language(language)

    def _convert_language(self, language):
        """Convert a language folder."""
        path = os.path.join(self.source_dir, language)

        if not os.path.isdir(path):
            log("Warning: Could not find language dir {}".format(language))

        for root, dirs, files in os.walk(path):
            rel_dir = root[len(self.source_dir):].lstrip('/')
            dirs.sort()
            for index_file_ext in ('md', 'tex'):
                index_filename = 'index.{}'.format(index_file_ext)
                if index_filename in files:
                    self._process_file(rel_dir, index_filename)

    def _process_file(self, rel_path, index_filename):
        full_path = os.path.join(self.source_dir, rel_path, index_filename)
        if os.path.isfile(full_path):
            print('processing {}'.format(full_path))
            ast = to_ast(full_path)
            out_full_path = os.path.join(
                self.source_dir, rel_path, 'index.json')
            with open(out_full_path, 'w') as out_file:
                json.dump(ast, out_file)

                # TODO: write this into output_dir!
