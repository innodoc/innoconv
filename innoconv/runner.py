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
            for content_file_ext in ('md', 'tex'):
                content_filename = 'content.{}'.format(content_file_ext)
                if content_filename in files:
                    self._process_file(rel_dir, content_filename)

    def _process_file(self, rel_path, content_filename):
        full_path = os.path.join(self.source_dir, rel_path, content_filename)
        if os.path.isfile(full_path):
            log('processing {}'.format(full_path))
            ast = to_ast(full_path)

            out_path = os.path.join(self.output_dir_base, rel_path)
            out_path_filename = os.path.join(out_path, 'content.json')
            os.makedirs(out_path, exist_ok=True)

            with open(out_path_filename, 'w') as out_file:
                json.dump(ast, out_file)
