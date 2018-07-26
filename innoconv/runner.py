"""Runner module"""

import json
import os

from innoconv.utils import to_ast, log


# TODO: create post-process module system
#  - copy static files
#  - generate TIK images
#  - concatenate Str and Space

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
            log("Writing language {} to {}".format(
                language, self.output_dir_base))
            self._convert_folder(language)

    def _convert_folder(self, language):
        """Convert a language folder."""
        path = os.path.join(self.source_dir, language)

        if not os.path.isdir(path):
            raise RuntimeError(
                "Warning: Could not find language dir {}".format(language))

        tree = {}

        for root, dirs, files in os.walk(path):
            rel_dir = root[len(self.source_dir):].lstrip(os.sep)

            dirs.sort()

            content_filename = 'content.{}'.format('md')
            if content_filename in files:
                self._process_file(rel_dir, content_filename, tree)

        tree = self._folder_to_json_tree(tree)
        log("Writing toc for {} to {}".format(
            language, self.output_dir_base))
        self._write_toc(language, tree)

    def _folder_to_json_tree(self, tree):
        newtree = []
        for key in sorted(tree.keys()):
            value = tree[key]
            tree_object = {
                'title': value[1],
                'id': key
            }
            if value[0]:
                tree_object['children'] = self._folder_to_json_tree(value[0])
            newtree.append(tree_object)
        return newtree

    def _write_toc(self, language, tree):
        out_path = os.path.join(self.output_dir_base, language)
        out_path_filename = os.path.join(out_path, 'toc.json')
        with open(out_path_filename, 'w') as out_file:
            json.dump(tree, out_file)

    def _process_file(self, rel_path, content_filename, tree):

        def _add_to_tree(tree, rel_path, title):
            """Add a folder to the fodler tree

            :param tree: The Object tree representign the File tree
            :type tree: dict

            :param rel_path: The relative path to the folder to add
            :type rel_path: str

            :param full_path: The full path to the content.md file to add
            :type full_path: str

            """

            folders = rel_path[3:].split(os.sep)
            current = tree
            for folder in folders:
                if folder:
                    if folder not in current:
                        current[folder] = [{}, title]
                    current = current[folder][0]

        full_path = os.path.join(self.source_dir, rel_path, content_filename)
        if os.path.isfile(full_path):
            log('processing {}'.format(full_path))
            ast, title = to_ast(full_path)

            _add_to_tree(tree, rel_path, title)

            out_path = os.path.join(self.output_dir_base, rel_path)
            out_path_filename = os.path.join(out_path, 'content.json')
            os.makedirs(out_path, exist_ok=True)

            with open(out_path_filename, 'w') as out_file:
                json.dump(ast, out_file)
