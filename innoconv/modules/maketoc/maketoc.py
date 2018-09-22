"""creates the toc.json file"""

import os

from innoconv.utils import write_json_file
from innoconv.modloader import AbstractModule
from innoconv.constants import TOC_FILENAME


def splitall(path):
    """Split path into directory components."""
    all_parts = []
    while 1:
        parts = os.path.split(path)
        if parts[1] == path:
            all_parts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            all_parts.insert(0, parts[1])
    return all_parts


class Maketoc(AbstractModule):
    """docstring for Maketoc."""

    def __init__(self):
        super(Maketoc, self).__init__()
        self.events.extend([
            'pre_conversion',
            'pre_language',
            'pre_content_file',
            'process_ast',
            'post_content_file',
            'post_language'
        ])
        self.rel_path = ''
        self.full_path = ''
        self.title = ''
        self.output_dir_base = ''
        self.language = ''
        self.tree = ''

    def pre_content_file(self, rel_path, full_path):
        """Stores the path for the next file we process"""
        self.rel_path = rel_path
        self.full_path = full_path

    def process_ast(self, ast):
        """read title from ast"""
        try:
            self.title = ast['meta']['title']['c']
        except KeyError:
            raise ValueError(
                "Missing title in meta block in {}".format(
                    self.full_path))

    def post_content_file(self):
        """add a file to the file tree"""
        self._add_to_tree()

    def pre_conversion(self, base_dirs):
        """store the output directory"""
        self.output_dir_base = base_dirs["output"]

    def pre_language(self, language):
        """create new tree, store language"""
        self.tree = []
        self.language = language

    def post_language(self):
        """format and write the toc"""

        self._write_toc()

    def _add_to_tree(self):
        path_components = splitall(self.rel_path)
        path_components.pop(0)  # language
        if not path_components:
            # this is the root section
            return
        children = self.tree
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
                    'title': self.title,
                })

    def _write_toc(self):
        out_path = os.path.join(self.output_dir_base, self.language)
        out_path_filename = os.path.join(out_path, TOC_FILENAME)
        write_json_file(out_path_filename, self.tree,
                        "Writing toc for {} to {}".format(
                            self.language, self.output_dir_base))
