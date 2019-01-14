# pylint: disable=line-too-long
"""

Content can include TikZ figures. They will be rendered to SVG and saved under
the folder ``_tikz`` in the static folder of the output directory.

TikZ blocks are then replaced by references to the generated SVG image.

-------
Example
-------

A TikZ figure is represented in the content like the following: ::

 ``\\begin{tikzpicture}[x=1.0cm, y=1.0cm]
    \\draw[thick, black] (-5.2,0) -- (6.2,0);
    \\foreach \\x in {-5, -4, ..., 6}
    \\draw[shift={(\\x,0)},color=black] (0pt,6pt) -- (0pt,-6pt)
    node[below=1.5pt] {\\normalsize $\\x$};
 \\end{tikzpicture}``

Upon conversion, this code block will be replaced in the output with an image
tag, like this: ::

![](/_tikz/tikz_00000.svg "Tikz Image")
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
\usepackage{{tikz}}
\begin{{document}}
\tikzset{{every picture/.style={{scale=1.0}}}}
{}
\end{{document}}
"""
CMD_PDFLATEX = ('pdflatex -halt-on-error -jobname {} -file-line-error --')
CMD_PDF2SVG = 'pdf2svg {} {}'


def _get_tikz_name(tikz_hash):
    return f'tikz_{tikz_hash}'


class Tikz2Svg(AbstractExtension):
    """This extension converts TikZ pictures to SVG files and embeds
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
            critical('Error: %i', pipe.returncode)
            critical(pipe.stdout.read().decode(ENCODING))
            raise RuntimeError("Tikz2Pdf: Error converting to PDF!")

    def _tikz_found(self, element):
        """Remember TikZ code and replace with image."""
        code = element['c'][1].strip()
        tikz_hash = md5(code.encode()).hexdigest()
        self._tikz_images[tikz_hash] = code
        filename = f'{_get_tikz_name(tikz_hash)}.svg'
        element['t'] = 'Image'
        element['c'] = [
            ['', [], []], [{'c': '', 't': 'Str'}],
            [join(TIKZ_FOLDER, filename), "TikZ Image"],
        ]
        info(f'Found TikZ image {filename}')

    def _process_ast_element(self, ast_element):
        """Process an element form the ast tree, navigating further down
        the tree if possible"""
        if isinstance(ast_element, list):
            for ast_sub_element in ast_element:
                self._process_ast_element(ast_sub_element)
            return
        try:
            try:
                if (ast_element['t'] == 'CodeBlock'
                        and 'tikz' in ast_element['c'][0][1]):
                    self._tikz_found(ast_element)
                    return
            except (TypeError, KeyError):
                pass
            for key in ast_element:
                self._process_ast_element(ast_element[key])
        except TypeError:
            pass

    def _render_and_copy_tikz(self):
        info(f"Compiling {len(self._tikz_images)} TikZ images.")
        if not self._tikz_images:
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
