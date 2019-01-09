# pylint: disable=line-too-long
r"""
Content can include Ti\ *k*\Z figures. They will be rendered to SVG and saved
in the folder ``_tikz`` in the static folder of the output directory.

Ti\ *k*\Z code blocks are replaced by image elements.

-------
Example
-------

A Ti\ *k*\Z image is written using a code block.

.. code-block:: latex

  ```tikz
  \\begin{tikzpicture}
  \\shade[left color=blue,right color=red,rounded corners=8pt] (-0.5,-0.5)
    rectangle (2.5,3.45);
  \\draw[white,thick,dashed,rounded corners=8pt] (0,0) -- (0,2) -- (1,3.25)
    -- (2,2) -- (2,0) -- (0,2) -- (2,2) -- (0,0) -- (2,0);
  \\node[white] at (1,-0.25) {\\footnotesize House of Santa Claus};
  \\end{tikzpicture}
  ```

Upon conversion, this code block will be replaced in the output with an image
tag, similar to the following.

.. code-block:: md

  ![](/_tikz/tikz_abcdef0123456789.svg "Alt text")
"""


from logging import critical, info

from os import mkdir
from os.path import join
from tempfile import TemporaryDirectory
from subprocess import Popen, PIPE
from distutils.dir_util import copy_tree
from hashlib import md5

from innoconv.extensions.abstract import AbstractExtension
from innoconv.constants import STATIC_FOLDER, TIKZ_FOLDER
from innoconv.constants import ENCODING

TEX_FILE_TEMPLATE = r"""
\documentclass{{standalone}}
\usepackage{{amsfonts}}
\usepackage{{tikz}}
\usetikzlibrary{{arrows,calc,decorations.pathmorphing}}
\begin{{document}}
\tikzset{{every picture/.style={{
  scale=1.4,every node/.style={{scale=1.4}}}}
}}
{}
\end{{document}}
"""
CMD_PDFLATEX = ('pdflatex -halt-on-error -jobname {} -file-line-error --')
CMD_PDF2SVG = 'pdf2svg {} {}'


def _get_tikz_name(tikz_hash):
    return f'tikz_{tikz_hash}'


class Tikz2Svg(AbstractExtension):
    r"""This extension converts Ti\ *k*\Z images to SVG files and embeds
    them in the content."""

    _helptext = "Convert TikZ code to SVG files."

    def __init__(self, *args, **kwargs):
        super(Tikz2Svg, self).__init__(*args, **kwargs)
        self._output_dir = None
        self._tikz_images = None

    @staticmethod
    def _run(cmd, cwd, stdin=None):
        pipe = Popen(
            cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd=cwd)
        if stdin:
            pipe.stdin.write(stdin.encode(ENCODING))
            pipe.stdin.close()
        pipe.wait()
        if pipe.returncode != 0:
            critical(cmd)
            critical(f"Error: {pipe.returncode}")
            critical("Printing program output for debugging:")
            critical(pipe.stdout.read().decode(ENCODING))
            if stdin:
                critical("Printing STDIN:")
                critical(stdin)
            raise RuntimeError("Tikz2Pdf: Error converting to PDF!")

    def _tikz_found(self, element, caption=None):
        """Remember TikZ code and replace with image."""
        code = element['c'][1].strip()
        tikz_hash = md5(code.encode()).hexdigest()
        self._tikz_images[tikz_hash] = code
        filename = f'{_get_tikz_name(tikz_hash)}.svg'
        element['t'] = 'Image'
        element['c'] = [
            ['', [], []],
            caption or [{'c': '', 't': 'Str'}],
            [join(TIKZ_FOLDER, filename), "TikZ Image"],
        ]
        info(f'Found TikZ image {filename}')

    def _process_ast_element(self, elem, parent=None):
        """Process an element form the AST and traverse its children."""
        def _parse_tikz(elem, parent):
            try:
                # parse caption
                if (parent and parent['t'] == 'Div' and
                        'figure' in parent['c'][0][1]):
                    if parent['c'][1][0]['t'] == 'Para':
                        caption = parent['c'][1].pop(0)['c']
                        self._tikz_found(elem, caption)
                        return
            except KeyError:
                pass
            self._tikz_found(elem)

        if isinstance(elem, list):
            for child in elem:
                self._process_ast_element(child, parent)
            return
        try:
            try:
                if elem['t'] == 'CodeBlock' and 'tikz' in elem['c'][0][1]:
                    _parse_tikz(elem, parent)
            except (TypeError, KeyError):
                pass
            for key in elem:
                self._process_ast_element(elem[key], elem)
        except TypeError:
            pass

    def _render_and_copy_tikz(self):
        info(f"Compiling {len(self._tikz_images)} TikZ images.")
        if len(self._tikz_images) < 1:
            return
        with TemporaryDirectory(prefix='innoconv-tikz2pdf-') as tmp_dir:
            pdf_path = join(tmp_dir, 'pdf_out')
            mkdir(pdf_path)
            svg_path = join(tmp_dir, 'svg_out')
            mkdir(svg_path)
            for tikz_hash, tikz_code in self._tikz_images.items():
                file_base = _get_tikz_name(tikz_hash)
                # generate tex document
                texdoc = TEX_FILE_TEMPLATE.format(tikz_code)
                # compile tex
                cmd = CMD_PDFLATEX.format(f'pdf_out/{file_base}')
                self._run(cmd, tmp_dir, stdin=texdoc)
                # convert to SVG
                pdf_filename = join(pdf_path, f'{file_base}.pdf')
                svg_filename = join(svg_path, f'{file_base}.svg')
                cmd = CMD_PDF2SVG.format(pdf_filename, svg_filename)
                self._run(cmd, tmp_dir)
            # copy SVG files
            tikz_path = join(self._output_dir, STATIC_FOLDER, TIKZ_FOLDER)
            copy_tree(svg_path, tikz_path, update=True)

    # extension events

    def start(self, output_dir, source_dir):
        """Initialize the list of images to be converted."""
        self._tikz_images = dict()
        self._output_dir = output_dir

    def pre_conversion(self, _):
        """Unused."""

    def pre_process_file(self, _):
        """Unused."""

    def post_process_file(self, ast, _):
        """Find TikZ images in AST and replace with image tags."""
        self._process_ast_element(ast)

    def post_conversion(self, _):
        """Unused."""

    def finish(self):
        """Render images and copy SVG files to the static folder."""
        self._render_and_copy_tikz()
