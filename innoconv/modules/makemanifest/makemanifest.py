"""creates the manifest.json file"""

import os
from yaml import load

from innoconv.modloader import AbstractModule
from innoconv.modules.maketoc.maketoc import splitall
from innoconv.utils import write_json_file
from innoconv.constants import (MANIFEST_FILENAME,
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
        self.paths = {
            'output': '',
            'source': ''
        }
        self.files = {
            'output': '',
            'source': ''
        }
        self.current_rel_path = ""
        self.current_full_path = ""
        self.current_title = ""

    def write_manifest(self):
        """Writes the manifest file"""

        write_json_file(self.files["output"], self.manifest,
                        "Wrote manifest: {}".format(self.files["output"]))

    def pre_conversion(self, base_dirs):
        """ Initialize new manifest """
        self.paths["output"] = base_dirs["output"]
        self.paths["source"] = base_dirs["source"]
        self.files["output"] = os.path.join(self.paths["output"],
                                            MANIFEST_FILENAME)
        self.files["source"] = os.path.join(self.paths["source"],
                                            MANIFEST_YAML_FILENAME)

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
        if not os.path.isfile(self.files["source"]):
            raise RuntimeError(
                "Error: Missing manifest.yaml")
        manifest_file = load(open(self.files["source"]))
        if not manifest_file:
            raise RuntimeError(
                "Error: Empty manifest.yaml")
        if 'languages' not in manifest_file:
            raise RuntimeError(
                "Error: Languages not defined in manifest.yaml")
        self.manifest['languages'] = manifest_file['languages']
        if 'title' not in manifest_file:
            raise RuntimeError(
                "Error: Title not defined in manifest.yaml")
        for lang in self.manifest['languages']:
            if lang not in manifest_file['title']:
                raise RuntimeError(
                    "Error: Title not defined for"
                    " language {} in manifest.yaml".format(lang))
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

    def load_languages(self, languages):
        """Replace the languages with the ones defined by the manifest"""
        self.load_manifest_yaml()
        languages.clear()
        languages.extend(self.get_languages())
