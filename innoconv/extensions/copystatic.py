"""
Content can include figures, images and videos. Static files can be included
in a special folder named ``_static``. The files will be copied to the
output directory automatically.

===========
Translation
===========

It's possible to have language-specific versions of a static file.

For that to work you need to have a ``_static`` folder beneath the language
folder. Files in this folder will take precedence over the common ``_static``
folder for that language.

**Example**: ``en/_static/example.png`` takes precedence over
``_static/example.png`` in the English version.

===============================
Relative and absolute reference
===============================

Files can be referenced using relative or absolute paths.

*Absolute paths* are resolved to the root folder, either the common
(``_static``) or language-specific (``en/_static``) folder.

*Relative paths* are resolved to the root folder but have the chapters path
fragment appended.

**Example**:
A reference to ``subdir/my_picture.png`` in ``/de/chapter01/content.md`` is
resolved to ``/de/_static/chapter01/subdir/my_picture.png`` whereas
``/subdir/my_picture.png`` (note the leading ``/``!) is resolved to
``/de/_static/subdir/my_picture.png``.
"""

import os.path
import os
import shutil
from urllib import parse

from innoconv.utils import log
from innoconv.extensions.abstract import AbstractExtension
from innoconv.constants import STATIC_FOLDER

ACCEPTED_LINK_CLASSES = (
    'video-static',
)


class CopyStatic(AbstractExtension):
    """This extension copies static files from the content source directory
    to the output directory."""

    _helptext = "Copies static files to the output folder."

    def __init__(self):
        super(CopyStatic, self).__init__()
        self.source_dir = None
        self.output_dir_base = None
        self.language = None
        self.languages = None
        self.to_copy = set()
        self.current_path = None

    # content parsing

    @staticmethod
    def _link_is_video(link_element):
        """Check if video is marked as local."""
        for cssclass in ACCEPTED_LINK_CLASSES:
            if cssclass in link_element['c'][0][1]:
                return True
        return False

    def _process_ast_array(self, ast_array):
        """Search every element in an AST array."""
        if not isinstance(ast_array, list):
            return
        for element in ast_array:
            self._process_ast_element(element)

    def _process_ast_element(self, ast_element):
        """Respond to elements that potentially reference static files."""
        if isinstance(ast_element, list):
            self._process_ast_array(ast_element)
        elif isinstance(ast_element, dict):
            if ast_element['t'] == 'Image':
                self._process_image(ast_element)
            elif ast_element['t'] == 'Link':
                self._process_link(ast_element)
            elif 'c' in ast_element:
                self._process_ast_array(ast_element['c'])

    def _process_link(self, link_element):
        """Links can reference local videos."""
        link = link_element['c'][2][0]
        content = link_element['c'][1]
        self._process_ast_array(content)
        if self._link_is_video(link_element):
            path = self._get_path(link)
            self.to_copy.add(path)

    def _process_image(self, image_element):
        link = image_element['c'][2][0]
        try:
            path = self._get_path(link)
            self.to_copy.add(path)
        except ValueError:
            pass

    def _get_path(self, path):
        """Check if a path linking to a remote ressource and for
        relative/absolute path."""
        if parse.urlparse(path).scheme:
            raise ValueError()
        if os.path.isabs(path):
            return path[1:]
        return os.path.join(
            # remove language part from relative path
            self.current_path.replace(self.language + os.path.sep, '', 1),
            path)

    # file copying

    def _copy_files(self):
        log("Copying {} static files:".format(len(self.to_copy)))

        def get_file_path(root_dir, path, lang=''):
            """Generate static file path."""
            return os.path.join(root_dir, lang, STATIC_FOLDER, path)

        for path in self.to_copy:
            for lang in self.languages:
                # localized version of file
                src = get_file_path(self.source_dir, path, lang)
                dst = get_file_path(self.output_dir_base, path, lang)
                if not os.path.isfile(src):
                    # common version as fallback
                    src = get_file_path(self.source_dir, path)
                    dst = get_file_path(self.output_dir_base, path)
                    if not os.path.isfile(src):
                        raise RuntimeError(
                            "Missing static file {}".format(path))
                # create folders as needed
                folder = os.path.dirname(dst)
                if not os.path.lexists(folder):
                    os.makedirs(folder)
                log(" copying file {} to {}".format(src, dst))
                shutil.copyfile(src, dst)

    # extension events

    def init(self, languages, output_dir_base, source_dir):
        """Remember languages and directories."""
        self.languages = languages
        self.output_dir_base = output_dir_base
        self.source_dir = source_dir

    def pre_conversion(self, language):
        """Remember current conversion language."""
        self.language = language

    def pre_process_file(self, path):
        """Remember file path."""
        self.current_path = path

    def post_process_file(self, ast):
        """Generate list of files to copy."""
        self._process_ast_array(ast)

    def post_conversion(self, language):
        """Unused."""
        pass

    def finish(self):
        """Finally copy the files."""
        self._copy_files()
