""" Copies the statci subfolder """

import os.path
import os
import shutil

from innoconv.utils import log
from innoconv.modloader import AbstractModule
from innoconv.constants import STATIC_FOLDER


class Copystatic(AbstractModule):
    """a Demo Module"""

    def __init__(self):
        super(Copystatic, self).__init__()
        self.root = ''
        self.target = ''
        self.language = ''
        self.languages = set()
        self.to_copy = set()
        self.current_path = {
            'rel_path': '',
            'full_path': ''
        }
        self.events.extend([
            'pre_language',
            "pre_conversion",
            "pre_content_file",
            "process_ast",
            "post_conversion"
        ])
        self.accepted_link_classes = [
            'video-static'
        ]

    def pre_language(self, language):
        """store the current language"""
        self.language = language
        self.languages.add(language)

    def pre_conversion(self, base_dirs):
        """store the output directory"""
        self.root = base_dirs["source"]
        self.target = base_dirs["output"]
        self.to_copy = set()

    def pre_content_file(self, rel_path, full_path):
        """Called before the parsing of a file"""
        self.current_path['rel_path'] = rel_path
        self.current_path['rel_path_nolang'] = rel_path.replace(
            self.language + os.path.sep,
            '',
            1)
        self.current_path['full_path'] = full_path

    def process_ast(self, ast):
        """Process the file's content"""
        self._process_ast_array(ast)

    def post_conversion(self):
        """Actually copy the files"""
        log('Copying {} static files:'.format(len(self.to_copy)))
        static_folders = []
        static_folders.append(os.path.join(
            self.target,
            STATIC_FOLDER))
        for lang in self.languages:
            static_folders.append(os.path.join(
                self.target,
                lang,
                STATIC_FOLDER))
        for folder in static_folders:
            if os.path.lexists(folder):
                shutil.rmtree(folder)
        for file in self.to_copy:
            log(' copying file {} to {}'.format(file[0], file[1]))
            folder = os.path.dirname(file[1])
            if not os.path.lexists(folder):
                os.makedirs(folder)
            shutil.copyfile(file[0], file[1])

    def _process_ast_array(self, ast_array):
        if not isinstance(ast_array, list):
            return
        for element in ast_array:
            self._process_ast_element(element)

    def _process_ast_element(self, ast_element):
        if isinstance(ast_element, list):
            self._process_ast_array(ast_element)
            return
        if not isinstance(ast_element, dict):
            return
        if ast_element['t'] == 'Image':
            self._process_image(ast_element)
        elif ast_element['t'] == 'Link':
            self._process_link(ast_element)
        elif 'c' in ast_element:
            self._process_ast_array(ast_element['c'])

    def _process_link(self, link_element):
        link = link_element['c'][2][0]
        content = link_element['c'][1]
        self._process_ast_array(content)
        if self._link_is_video(link_element):
            path = self._get_path(link)
            if not path:
                return
            self._copy_file(path)

    def _process_image(self, image_element):
        link = image_element['c'][2][0]
        path = self._get_path(link)
        if not path:
            return
        self._copy_file(path)

    def _link_is_video(self, link_element):
        for cssclass in self.accepted_link_classes:
            if cssclass in link_element['c'][0][1]:
                return True
        return False

    def _get_path(self, path):
        if (path.startswith('http://') or
                path.startswith('https://') or
                path.startswith('ftp://')):
            return ''
        new_path = path.replace('/', os.path.sep)
        if path.startswith('/'):
            return new_path[1:]
        return os.path.join(
            self.current_path['rel_path_nolang'], new_path)

    def _copy_file(self, path):
        localized_path = os.path.join(
            self.root,
            self.language,
            STATIC_FOLDER,
            path)
        general_path = os.path.join(
            self.root,
            STATIC_FOLDER,
            path)
        if os.path.isfile(localized_path):
            from_path = localized_path
            to_path = os.path.join(
                self.target,
                self.language,
                STATIC_FOLDER,
                path)
        elif os.path.isfile(general_path):
            from_path = general_path
            to_path = os.path.join(
                self.target,
                STATIC_FOLDER,
                path)
        else:
            raise RuntimeError(
                "Missing static file {} referenced in {}".format(
                    path,
                    self.current_path['rel_path']))
        self.to_copy.add((from_path, to_path))
