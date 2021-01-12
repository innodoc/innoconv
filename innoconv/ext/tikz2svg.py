r"""
Convert and insert Ti\ *k*\Z figures.

SVG files are rendered from Ti\ *k*\Z code and saved in the folder ``_tikz`` in
the static folder of the output directory.

Ti\ *k*\Z code blocks are replaced by image elements.

.. note::

    In order to use this extension you need to have the following software
    installed on your system:

    * LaTeX distribution with PGF/Ti\ *k*\Z
    * `pdf2svg <https://github.com/dawbarton/pdf2svg>`_

-------
Example
-------
A Ti\ *k*\Z image is directly embedded into Markdown using a code block.

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

During conversion the code block will be turned into an image tag, similar
to the following.

.. code-block:: md

  ![](/_tikz/tikz_abcdef0123456789.svg "Alt text")

"""


from hashlib import md5
from logging import critical, info
from os import mkdir
from os.path import join
from shutil import copytree, rmtree
from subprocess import PIPE, Popen
from tempfile import TemporaryDirectory

from innoconv.constants import ENCODING, STATIC_FOLDER
from innoconv.ext.abstract import AbstractExtension
from innoconv.traverse_ast import TraverseAst

TEX_FILE_TEMPLATE = r"""
\documentclass{{standalone}}
\usepackage{{tikz}}
{preamble}
\begin{{document}}
\tikzset{{every picture/.style={{
  scale=1.4,every node/.style={{scale=1.4}}}}
}}
{tikz_code}
\end{{document}}
"""
CMD_PDFLATEX = "pdflatex -halt-on-error -jobname {} -file-line-error --"
CMD_PDF2SVG = "pdf2svg {} {}"
TIKZ_FOLDER = "_tikz"
TIKZ_FILENAME = "tikz_{}"
TIKZ_IMG_TAG_ALT = "TikZ Image"


class Tikz2Svg(AbstractExtension):
    r"""Convert and insert Ti\ *k*\Z images."""

    _helptext = "Convert TikZ code to SVG files."

    def __init__(self, *args, **kwargs):
        """Initialize variables."""
        super().__init__(*args, **kwargs)
        self._output_dir = None
        self._tikz_images = None

    @staticmethod
    def _run(cmd, cwd, stdin=None):
        pipe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd=cwd)
        if stdin:
            pipe.stdin.write(stdin.encode(ENCODING))
            pipe.stdin.close()
        pipe.wait()
        if pipe.returncode != 0:
            critical(cmd)
            critical("Error: %d", pipe.returncode)
            critical("Printing program stdout:")
            critical(pipe.stdout.read().decode(ENCODING))
            critical("Printing program stderr:")
            critical(pipe.stderr.read().decode(ENCODING))
            raise RuntimeError("Tikz2Pdf: Error converting to PDF!")

    @staticmethod
    def _get_tikz_name(tikz_hash):
        return TIKZ_FILENAME.format(tikz_hash)

    def _tikz_found(self, element, caption=None):
        """Remember TikZ code and replace with image."""
        code = element["c"][1].strip()
        tikz_hash = md5(code.encode()).hexdigest()
        self._tikz_images[tikz_hash] = code
        filename = f"{Tikz2Svg._get_tikz_name(tikz_hash)}.svg"
        element["t"] = "Image"
        element["c"] = [
            ["", [], []],
            caption or [],
            [join(TIKZ_FOLDER, filename), TIKZ_IMG_TAG_ALT],
        ]
        info("Found TikZ image %s", filename)

    def _parse_tikz(self, elem, parent):
        try:
            if (
                parent
                and parent["t"] == "Div"
                and "figure" in parent["c"][0][1]
                and parent["c"][1][0]["t"] == "Para"
            ):
                caption = parent["c"][1].pop(0)["c"]
                self._tikz_found(elem, caption)
                return
        except KeyError:
            pass
        self._tikz_found(elem)

    def _render_and_copy_tikz(self):
        info("Compiling %d TikZ images.", len(self._tikz_images))
        if not self._tikz_images:
            return
        with TemporaryDirectory(prefix="innoconv-tikz2pdf-") as tmp_dir:
            pdf_path = join(tmp_dir, "pdf_out")
            mkdir(pdf_path)
            svg_path = join(tmp_dir, "svg_out")
            mkdir(svg_path)
            for tikz_hash, tikz_code in self._tikz_images.items():
                file_base = Tikz2Svg._get_tikz_name(tikz_hash)
                # generate tex document
                try:
                    preamble = self._manifest.tikz_preamble
                except AttributeError:
                    preamble = ""
                # as this template is used with .format() we need to escape
                # curly brackets
                preamble.replace("{", "{{")
                preamble.replace("}", "}}")
                texdoc = TEX_FILE_TEMPLATE.format(
                    tikz_code=tikz_code, preamble=preamble
                )
                info("Compiling %s", file_base)
                # compile tex
                cmd = CMD_PDFLATEX.format(join("pdf_out", file_base))
                self._run(cmd, tmp_dir, stdin=texdoc)
                # convert to SVG
                pdf_filename = join(pdf_path, f"{file_base}.pdf")
                svg_filename = join(svg_path, f"{file_base}.svg")
                cmd = CMD_PDF2SVG.format(pdf_filename, svg_filename)
                self._run(cmd, tmp_dir)
            # copy SVG files
            tikz_path = join(self._output_dir, STATIC_FOLDER, TIKZ_FOLDER)
            try:
                copytree(svg_path, tikz_path)
            except FileExistsError:
                rmtree(tikz_path)
                copytree(svg_path, tikz_path)

    def process_element(self, elem, parent):
        """Respond to AST element."""
        try:
            if elem["t"] == "CodeBlock" and "tikz" in elem["c"][0][1]:
                self._parse_tikz(elem, parent)
        except (TypeError, KeyError):
            pass

    # extension events

    def start(self, output_dir, source_dir):
        """Initialize the list of images to be converted."""
        self._tikz_images = dict()
        self._output_dir = output_dir

    def post_process_file(
        self, ast, title, content_type, section_type=None, short_title=None
    ):
        """Find TikZ images in AST and replace with image tags."""
        TraverseAst(self.process_element).traverse(ast)

    def finish(self):
        """Render images and copy SVG files to the static folder."""
        self._render_and_copy_tikz()
