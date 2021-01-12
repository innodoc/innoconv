"""
Extension that copies static files.

Content can include figures, images and videos. Static files can be included
in a special folder named :file:`_static`. The files will be copied to the
output directory automatically.

===========
Translation
===========
It's possible to have language-specific versions of a static file.

For that to work you need to have a :file:`_static` folder beneath the language
folder. Files in this folder will take precedence over the common
:file:`_static` folder for that language.

**Example**: :file:`en/_static/example.png` takes precedence over
:file:`_static/example.png` in the English version.

===============================
Relative and absolute reference
===============================
Files can be referenced using relative or absolute paths.

*Absolute paths* are resolved to the root folder, either the common
(:file:`_static`) or language-specific (:file:`en/_static`) folder.

*Relative paths* are resolved to the root folder but have the chapters path
fragment appended.

-------
Example
-------
This example shows how a reference to an image is resolved. The references
happen inside the section ``chapter01`` in the English language version.

+----------+------------------------------------------------+
| Type     | Resolution                                     |
+==========+================================================+
| Relative | ``subdir/my_picture.png`` →                    |
|          | ``en/_static/chapter01/subdir/my_picture.png`` |
+----------+------------------------------------------------+
| Absolute | ``/subdir/my_picture.png`` →                   |
|          | ``en/_static/subdir/my_picture.png``           |
+----------+------------------------------------------------+

"""

import logging
import os
import os.path
import shutil
from urllib import parse

from innoconv.constants import LOGO_EXTENSIONS, STATIC_FOLDER
from innoconv.ext.abstract import AbstractExtension
from innoconv.traverse_ast import TraverseAst

VIDEO_CLASS = "video-static"


class CopyStatic(AbstractExtension):
    """
    Copy static files to the output folder.

    This extension copies checks the AST for references to static files and
    copies them from the content source directory to the output directory.
    """

    _helptext = "Copy static files to the output folder."

    def __init__(self, *args, **kwargs):
        """Initialize variables."""
        super().__init__(*args, **kwargs)
        self._source_dir = None
        self._output_dir = None
        self._current_language = None
        self._to_copy = set()
        self._current_path = None
        self._logo_filename = None

    # content parsing

    def _process_link(self, link_element):
        """Check if link is a video reference."""
        link = link_element["c"][2][0]
        if VIDEO_CLASS in link_element["c"][0][1]:
            try:
                link_element["c"][2][0] = self._add_static_from_section(link)
            except ValueError:
                pass

    def _process_image(self, image_element):
        link = image_element["c"][2][0]
        try:
            image_element["c"][2][0] = self._add_static_from_section(link)
        except ValueError:
            pass

    def _add_static_from_section(self, orig_path):
        # skip remote resource
        if parse.urlparse(orig_path).scheme:
            raise ValueError()
        # relative to section?
        if orig_path[0] == "/":
            ref_path = orig_path[1:]
            section_path = ""
        else:
            ref_path = orig_path
            section_path = self._current_path[3:]  # strip language
            if section_path:
                section_path = f"{section_path.strip('/')}/"
        return self._add_static(ref_path, section_path)

    def _add_static(self, ref_path, section_path=""):
        """Remember paths to copy and rewrite URL."""

        def _get_src_file_path(root_dir, _path, _sec_path, lang=""):
            return os.path.join(root_dir, lang, STATIC_FOLDER, _sec_path, _path)

        def _get_dest_file_path(root_dir, _path, _sec_path, lang=""):
            if lang:
                lang = f"_{lang}"
            return os.path.join(root_dir, STATIC_FOLDER, lang, _sec_path, _path)

        # localized version
        src = _get_src_file_path(
            self._source_dir, ref_path, section_path, self._current_language
        )
        dst = _get_dest_file_path(
            self._output_dir, ref_path, section_path, self._current_language
        )
        rewritten = f"_{self._current_language}/{section_path}{ref_path}"
        if not os.path.isfile(src):
            # common version
            src = _get_src_file_path(self._source_dir, ref_path, section_path)
            dst = _get_dest_file_path(self._output_dir, ref_path, section_path)
            rewritten = f"{section_path}{ref_path}"
            if not os.path.isfile(src):
                raise RuntimeError(f"Missing static file {ref_path}")

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

    def _add_logo(self):
        for ext in LOGO_EXTENSIONS:
            try:
                logo_filename = f"_logo.{ext}"
                self._add_static(logo_filename)
                self._logo_filename = logo_filename
                logging.info("Logo %s copied.", logo_filename)
                return
            except RuntimeError:
                continue
        logging.info("No Logo found.")

    def process_element(self, elem, _):
        """Respond to AST element."""
        if elem["t"] == "Image":
            self._process_image(elem)
        elif elem["t"] == "Link":
            self._process_link(elem)

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

    def post_process_file(
        self, ast, title, content_type, section_type=None, short_title=None
    ):
        """Find all static files in AST."""
        TraverseAst(self.process_element).traverse(ast)

    def finish(self):
        """Copy static files to the output folder."""
        self._add_logo()
        self._copy_files()

    def manifest_fields(self):
        """Add `logo` field to manifest."""
        return {"logo": self._logo_filename} if self._logo_filename else {}
