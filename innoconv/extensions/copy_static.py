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

-------
Example
-------

This example shows how a reference to an image is resolved. The references
happen inside the section ``chapter01`` in the English language version.

+----------+------------------------------+------------------------------------------------+
| Type     | Reference                    | Resolved to                                    |
+==========+==============================+================================================+
| Relative | ``subdir/my_picture.png``    | ``en/_static/chapter01/subdir/my_picture.png`` |
+----------+------------------------------+------------------------------------------------+
| Absolute | | ``/subdir/my_picture.png`` | ``en/_static/subdir/my_picture.png``           |
|          | | (with leading ``/``)       |                                                |
+----------+------------------------------+------------------------------------------------+
"""  # noqa: E501

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

    def _process_ast_element(self, ast_element, ast_type):
        if ast_type == 'Image':
            self._process_image(ast_element)
        elif ast_type == 'Link':
            self._process_link(ast_element)

    def _process_link(self, link_element):
        """Links can reference local videos."""
        link = link_element['c'][2][0]
        if self._link_is_video(link_element):
            try:
                link_element['c'][2][0] = self._add_static(link)
            except ValueError:
                pass

    def _process_image(self, image_element):
        link = image_element['c'][2][0]
        try:
            image_element['c'][2][0] = self._add_static(link)
        except ValueError:
            pass

    def _add_static(self, orig_path):
        """Remember paths to copy and rewrite URL."""
        def _get_src_file_path(root_dir, _path, _sec_path, lang=''):
            return os.path.join(
                root_dir, lang, STATIC_FOLDER, _sec_path, _path)

        def _get_dest_file_path(root_dir, _path, _sec_path, lang=''):
            if lang:
                lang = '_{}'.format(lang)
            return os.path.join(
                root_dir, STATIC_FOLDER, lang, _sec_path, _path)

        # skip remote resource
        if parse.urlparse(orig_path).scheme:
            raise ValueError()

        # relative to section?
        if orig_path[0] == '/':
            ref_path = orig_path[1:]
            section_path = ''
        else:
            ref_path = orig_path
            section_path = self._current_path[3:]  # strip language
            if section_path:
                section_path = '{}/'.format(section_path.strip('/'))

        # localized version
        src = _get_src_file_path(
            self._source_dir, ref_path, section_path, self._current_language)
        dst = _get_dest_file_path(
            self._output_dir, ref_path, section_path, self._current_language)
        rewritten = '_{}/{}{}'.format(
            self._current_language, section_path, ref_path)
        if not os.path.isfile(src):
            # common version
            src = _get_src_file_path(self._source_dir, ref_path, section_path)
            dst = _get_dest_file_path(self._output_dir, ref_path, section_path)
            rewritten = '{}{}'.format(section_path, ref_path)
            if not os.path.isfile(src):
                msg = "Missing static file {}".format(orig_path)
                raise RuntimeError(msg)

        self._to_copy.add((src, dst))
        return rewritten

    # file copying
    def _copy_files(self):
        logging.info("%d files found.", len(self._to_copy))
        for src, dst in self._to_copy:
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

    def process_ast_array(self, ast_array, parent_element):
        """Unused."""

    def process_ast_element(self, ast_element, ast_type, parent_element):
        """Generate list of files to copy."""
        self._process_ast_element(ast_element, ast_type)

    def post_process_file(self, ast, _):
        """Unused."""

    def post_conversion(self, language):
        """Unused."""

    def finish(self):
        """Finally copy the files."""
        self._copy_files()
