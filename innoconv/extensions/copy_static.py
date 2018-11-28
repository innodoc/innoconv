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

import logging
import os.path
import os
import shutil
from urllib import parse

from innoconv.extensions.abstract import AbstractExtension
from innoconv.constants import STATIC_FOLDER

ACCEPTED_LINK_CLASSES = (
    'video-static',
)


class CopyStatic(AbstractExtension):
    """Copy static files from the content source directory to the output
    directory.
    """

    _helptext = "Copy static files to the output folder."

    def __init__(self, *args, **kwargs):
        super(CopyStatic, self).__init__(*args, **kwargs)
        self._source_dir = None
        self._output_dir = None
        self._current_language = None
        self._to_copy = set()
        self._current_path = None

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
            try:
                path = self._get_path(link)
                self._to_copy.add(path)
            except ValueError:
                pass

    def _process_image(self, image_element):
        link = image_element['c'][2][0]
        try:
            path = self._get_path(link)
            self._to_copy.add(path)
        except ValueError:
            pass

    def _get_path(self, path):
        """Build resulting copy path from resource reference."""
        # remote resource
        if parse.urlparse(path).scheme:
            raise ValueError()
        # absolute (relative to static folder)
        if os.path.isabs(path):
            return path[1:]
        # relative (prefixed with section path)
        path_prefix = self._current_path.replace(self._current_language, '', 1)
        path_prefix = path_prefix.rstrip('/')
        return os.path.join(path_prefix, path).lstrip('/')

    # file copying

    def _copy_files(self):
        def get_file_path(root_dir, path, lang=''):
            """Generate static file path."""
            return os.path.join(root_dir, lang, STATIC_FOLDER, path)

        logging.info("%d files found.", len(self._to_copy))
        for path in self._to_copy:
            for lang in self._manifest.languages:
                # localized version of file
                src = get_file_path(self._source_dir, path, lang)
                dst = get_file_path(self._output_dir, path, lang)
                if not os.path.isfile(src):
                    # common version as fallback
                    src = get_file_path(self._source_dir, path)
                    dst = get_file_path(self._output_dir, path)
                    if not os.path.isfile(src):
                        msg = "Missing static file {}".format(path)
                        raise RuntimeError(msg)
                # create folders as needed
                folder = os.path.dirname(dst)
                if not os.path.lexists(folder):
                    os.makedirs(folder)
                logging.info(" %s -> %s", src, dst)
                shutil.copyfile(src, dst)

    # extension events

    def start(self, output_dir, source_dir):
        """Remember directories."""
        self._output_dir = output_dir
        self._source_dir = source_dir

    def pre_conversion(self, language):
        """Remember current conversion language."""
        self._current_language = language

    def pre_process_file(self, path):
        """Remember file path."""
        self._current_path = path

    def post_process_file(self, ast, _):
        """Generate list of files to copy."""
        self._process_ast_array(ast)

    def post_conversion(self, language):
        """Unused."""

    def finish(self):
        """Finally copy the files."""
        self._copy_files()
