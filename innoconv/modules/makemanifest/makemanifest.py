"""creates the manifest.json file"""

import os
from yaml import load

from innoconv.modloader import AbstractModule
from innoconv.modules.maketoc.maketoc import splitall
from innoconv.utils import write_json_file
from innoconv.constants import (MANIFEST_FILENAME,
                                STATIC_FOLDER,
                                MANIFEST_YAML_FILENAME)


class Makemanifest(AbstractModule):
    """creates the manifest.json file"""

    def __init__(self):
        super(Makemanifest, self).__init__()

        self.events.extend([
            'pre_conversion',
            'pre_content_file',
            'process_ast',
            'post_content_file',
            'post_conversion'
        ])

        self.manifest = {
            'languages': [],
            'title': {},
            'toc': []
        }
        self.output_path = ""
        self.output_filname = ""
        self.static_folder = ""
        self.current_rel_path = ""
        self.current_full_path = ""
        self.current_title = ""

    def write_manifest(self):
        """Writes the manifest file"""

        write_json_file(self.output_filname, self.manifest,
                        "Wrote manifest: {}".format(self.output_filname))

    def pre_conversion(self, base_dirs):
        """ Initialize new manifest """
        self.output_path = base_dirs["output"]
        self.output_filname = os.path.join(self.output_path, MANIFEST_FILENAME)
        self.static_folder = os.path.join(base_dirs["source"], STATIC_FOLDER)

    def _has_folder(self, folder_name, file_name):
        folder = os.path.join(self.static_folder, folder_name)
        if not os.path.isdir(folder):
            return False
        for lang in self.manifest['languages']:
            filename = lang + "_" + file_name
            file_path = os.path.join(folder, filename)
            if not os.path.isfile(file_path):
                return False
        return True

    def pre_content_file(self, rel_path, full_path):
        """sets the path for the current files"""
        self.current_rel_path = rel_path
        self.current_full_path = full_path

    def process_ast(self, ast):
        """read title from ast"""
        try:
            self.current_title = ast['meta']['title']['c']
        except KeyError:
            raise ValueError(
                "Missing title in meta block in {}".format(
                    self.current_full_path))

    def post_content_file(self):
        """Completes a file"""
        path_components = splitall(self.current_rel_path)
        lang = path_components.pop(0)  # language
        if not path_components:
            # this is the root section
            self.manifest['title'][lang] = self.current_title
            return
        children = self.manifest['toc']
        found = None
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
                    'title': {
                        lang: self.current_title
                    }
                })
        if found:
            found['title'][lang] = self.current_title

    def load_manifest_yaml(self):
        """"Loads the manifest.yaml file"""
        manifest_file = load(open(MANIFEST_YAML_FILENAME))
        self.manifest['languages'] = manifest_file['languages']
        for lang in self.manifest['languages']:
            self.manifest['title'][lang] = manifest_file['title'][lang]

    def get_toc(self):
        """Retrives the Tree of Contents"""
        return self.manifest['toc']

    def get_title(self):
        """Retrives the Title"""
        return self.manifest['title']

    def get_languages(self):
        """Retrives the Languages"""
        return self.manifest['languages']

    def post_conversion(self):
        """concludes everything"""
        self.write_manifest()

    def _has_file(self, file_name):
        file_path = os.path.join(self.static_folder, file_name)
        if not os.path.isfile(file_path):
            return False
        return True

    def get_pages(self):
        """Retrives the pages"""
        return self.manifest['pages']

    def load_languages(self, languages):
        """Replace the languages with the ones defined by the manifest"""
        self.load_manifest_yaml()
        languages.clear()
        languages.extend(self.get_languages())
