# pylint: disable=line-too-long
"""

Content can include TikZ figures. They will be rendered to SVG and saved in a
special folder ``_tikz`` in the folder ``_static`` in the output directory.
At the same time, the TikZ blocks in the content get replaced with references
to the generated images.


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

from os import chdir, getcwd, mkdir
from os.path import join
from tempfile import TemporaryDirectory
from subprocess import Popen, PIPE
from distutils.dir_util import copy_tree

from innoconv.extensions.abstract import AbstractExtension
from innoconv.constants import STATIC_FOLDER, TIKZ_FOLDER, TIKZ_FILENAME
from innoconv.constants import ENCODING

LATEX_BOILERPLATE = r"""
\documentclass[border=2bp]{standalone}
\usepackage{tikz}
\usetikzlibrary{external}
\tikzexternalize[prefix=figures/]
\begin{document}
\begingroup
\tikzset{every picture/.style={scale=1}}

%(content)s

\endgroup
\end{document}
"""

PDFLATEX = 'pdflatex --shell-escape -file-line-error -interaction=nonstopmode'


def run(cmd, stdin=None):
    """util to run command in a subprocess, and communicate with it."""
    pipe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    if stdin:
        pipe.stdin.write(stdin.encode(ENCODING))
        pipe.stdin.close()
    pipe.wait()

    # error out if necessary
    if pipe.returncode != 0:
        critical(cmd)
        critical('Error: %i', pipe.returncode)
        critical(pipe.stderr.read().decode(ENCODING))
        raise RuntimeError("Tikz2Pdf: Error when converting Latex to PDF")

    return pipe.stdout.read().decode(ENCODING)


class Tikz2Svg(AbstractExtension):
    """This extension converts TikZ images to svg images, and embeds
    them in the content"""

    _helptext = "Converts TikZ to SVG"

    def __init__(self, *args, **kwargs):
        super(Tikz2Svg, self).__init__(*args, **kwargs)
        self.output_dir_base = None
        self.tmp_dir = None
        self.tikz_images = None
        self.figures_path = None
        self.svgs_path = None

    def replace_tikz_element(self, element):
        """replaces a tikz image with a reference to the image"""
        tikz_code = element['c'][1]
        self.tikz_images.append(tikz_code)
        filename = TIKZ_FILENAME.format(len(self.tikz_images)-1)
        filename = '/'+join(TIKZ_FOLDER, filename)
        element['t'] = "Image"
        element['c'] = [
            ["", [], []], [{'c': '', 't': 'Str'}],
            [filename, "TikZ Image"]
        ]
        info('Found TikZ image # %i', len(self.tikz_images)-1)

    # Navigating ast

    def _process_ast_element(self, ast_element):
        """Process an element form the ast tree, navigating further down
        the tree if possible"""
        if isinstance(ast_element, list):
            for ast_sub_element in ast_element:
                self._process_ast_element(ast_sub_element)
            return
        try:
            try:
                if (ast_element["t"] == "CodeBlock"
                        and ast_element["c"][0][1][0] == "tikz"):
                    self.replace_tikz_element(ast_element)
                    return
            except (TypeError, KeyError):
                pass
            for key in ast_element:
                self._process_ast_element(ast_element[key])
        except TypeError:
            pass

    # Create Files

    def _create_tex(self, directory):
        filename = join(directory, 'input.tex')
        content = ""
        for i, tikz in enumerate(self.tikz_images):
            content += "\n\n"
            content += "\\tikzsetnextfilename{{tkiz_{0:05d}}}".format(i)
            content += "\n"
            content += tikz
        doc = LATEX_BOILERPLATE % {'content': content}
        with open(filename, 'w+') as file:
            file.write(doc)
        return doc

    def _create_pdfs(self, directory):
        self.figures_path = join(directory, 'figures')
        mkdir(self.figures_path)
        run(PDFLATEX + ' input.tex')

    def _create_svgs(self, directory):
        self.svgs_path = join(directory, 'svgs')
        mkdir(self.svgs_path)
        for i, _ in enumerate(self.tikz_images):
            self._create_svg(i)

    def _create_svg(self, i):
        pdf_filename = join(self.figures_path, 'tkiz_{0:05d}.pdf'.format(i))
        svg_filename = join(self.svgs_path, TIKZ_FILENAME.format(i))
        pdf2svg = 'pdf2svg {} {}'.format(pdf_filename, svg_filename)
        run(pdf2svg)

    def _copy_svgs(self):
        tikz_path = join(self.output_dir_base, STATIC_FOLDER, TIKZ_FOLDER)
        copy_tree(self.svgs_path, tikz_path, update=1)

    def create_files(self, directory):
        """Creates a tex file, converts it to pdfs, converts those to svgs and
        finally copies them to the right folder"""
        self._create_tex(directory)
        self._create_pdfs(directory)
        self._create_svgs(directory)
        self._copy_svgs()

    # extension events

    def start(self, output_dir, source_dir):
        """Initializes the list of images to be converted."""
        self.tikz_images = list()
        self.output_dir_base = output_dir

    def pre_conversion(self, _):
        """Unused."""

    def pre_process_file(self, _):
        """Unused."""

    def post_process_file(self, ast, _):
        """Reads TikZ from AST and repalces it with an image tag."""
        self._process_ast_element(ast)

    def post_conversion(self, _):
        """Unused."""

    def finish(self):
        """Renders the images into a temporary folder and copies svg files to
        _static"""
        current_dir = getcwd()
        with TemporaryDirectory(prefix='innoconv-tikz2pdf-') as temp_directory:
            chdir(temp_directory)
            self.create_files(temp_directory)
            chdir(current_dir)

        info('Create %i TikZ images', len(self.tikz_images))
