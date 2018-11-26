"""
Converts TikZ images in the content to SVG
"""
from os import chdir, getcwd, mkdir
from os.path import join
from tempfile import TemporaryDirectory
from subprocess import Popen, PIPE
from distutils.dir_util import copy_tree

from innoconv.extensions.abstract import AbstractExtension
from innoconv.constants import STATIC_FOLDER, TIKZ_FOLDER, TIKZ_FILENAME
from innoconv.constants import ENCODING
from innoconv.utils import log

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
        pipe.stdin.write(stdin.encode('utf-8'))
        pipe.stdin.close()
    pipe.wait()

    # error out if necessary
    if pipe.returncode != 0:
        log(getcwd())
        log('>', cmd)
        log('Error.')
        log('-' * 20, 'STDIN')
        log(stdin)
        log('-' * 20, 'STDOUT')
        log(pipe.stdout.read().decode(ENCODING))
        log('-' * 20, 'STDERR')
        log(pipe.stderr.read().decode(ENCODING))
        raise RuntimeError("Tikz2Pdf: Error when converting Latex to PDF")

    return pipe.stdout.read()


class Tikz2Pdf(AbstractExtension):
    """This extension converts TikZ images to svg images, and embeds
    them in the content"""

    _helptext = "Converts TikZ to SVG"

    def __init__(self):
        super(Tikz2Pdf, self).__init__()
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
        filename = join(STATIC_FOLDER, TIKZ_FOLDER, filename)
        element['t'] = "Image"
        element['c'] = [
            ["", [], []], [{"t": "Str", "c": tikz_code}],
            [filename, ""]
        ]

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
                if (ast_element["t"] == "CodeBlock" and
                        ast_element["c"][0][1][0] == "tikz"):
                    self.replace_tikz_element(ast_element)
                    return
            except (TypeError, KeyError):
                pass
            for key in ast_element:
                self._process_ast_element(ast_element[key])
        except TypeError:
            pass

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

    # extension events

    def init(self, languages, output_dir_base, source_dir):
        """Unused."""
        self.tikz_images = list()
        self.output_dir_base = output_dir_base

    def pre_conversion(self, language):
        """Unused."""
        pass

    def pre_process_file(self, path):
        """Unused."""
        pass

    def post_process_file(self, ast, _):
        """Unused."""
        self._process_ast_element(ast)

    def post_conversion(self, language):
        """Unused."""
        pass

    def finish(self):
        """Unused."""
        current_dir = getcwd()
        with TemporaryDirectory(prefix='innoconv-tikz2pdf-') as temp_directory:
            chdir(temp_directory)
            self._create_tex(temp_directory)
            self._create_pdfs(temp_directory)
            self._create_svgs(temp_directory)
            self._copy_svgs()
            chdir(current_dir)
