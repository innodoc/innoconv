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
from os import makedirs
from os.path import join
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
  scale=2.0,every node/.style={{scale=2.0}}}}
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
        self._tikz_images = {}

    @staticmethod
    def _run(cmd, cwd, cmd_input=None):
        with Popen(
            cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd=cwd
        ) as pipe:
            if pipe.stdin is None or pipe.stdout is None or pipe.stderr is None:
                raise RuntimeError("Failed to open pipe!")

            if cmd_input is not None:
                pipe.stdin.write(cmd_input)
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
                self._tikz_found(elem, caption=caption)
                return
        except KeyError:
            pass
        self._tikz_found(elem)

    def _get_texdoc(self, tikz_code):
        """Generate tex document from TikZ code."""
        try:
            preamble = self._manifest.tikz_preamble
        except AttributeError:
            preamble = ""
        # as this template is used with .format() we need to escape
        # curly brackets
        preamble.replace("{", "{{")
        preamble.replace("}", "}}")
        return TEX_FILE_TEMPLATE.format(tikz_code=tikz_code, preamble=preamble)

    def _render_svg(self, tikz_hash, tikz_code):
        if self._output_dir is None:
            raise RuntimeError("output dir is None!")

        texdoc = self._get_texdoc(tikz_code)
        file_base = Tikz2Svg._get_tikz_name(tikz_hash)

        with TemporaryDirectory(prefix=f"innoconv-tikz2pdf-{tikz_hash}-") as tmp_dir:
            # Generate PDF from TikZ code
            pdflatex_cmd = CMD_PDFLATEX.format(file_base)

            # Convert PDF to SVG
            pdf_filename = join(tmp_dir, f"{file_base}.pdf")
            svg_filename = join(tmp_dir, f"{file_base}.svg")
            self._run(pdflatex_cmd, tmp_dir, cmd_input=texdoc.encode(ENCODING))
            pdf2svg_cmd = CMD_PDF2SVG.format(pdf_filename, svg_filename)
            self._run(pdf2svg_cmd, tmp_dir)
            with open(svg_filename, "r", encoding=ENCODING) as svg_file:
                svg_code = svg_file.read()

        # save SVG file
        tikz_path = join(self._output_dir, STATIC_FOLDER, TIKZ_FOLDER)
        svg_filename = join(tikz_path, f"{file_base}.svg")
        makedirs(tikz_path, exist_ok=True)
        with open(svg_filename, "w", encoding=ENCODING) as svg_file:
            svg_file.write(svg_code)

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
        self._tikz_images = {}
        self._output_dir = output_dir

    def post_process_file(
        self, ast, title, content_type, section_type=None, short_title=None
    ):
        """Find TikZ images in AST and replace with image tags."""
        TraverseAst(self.process_element).traverse(ast)

    def finish(self):
        """Render images and copy SVG files to the static folder."""
        info("Compiling %d TikZ images.", len(self._tikz_images))
        if not self._tikz_images:
            return

        for tikz_hash, tikz_code in self._tikz_images.items():
            self._render_svg(tikz_hash, tikz_code)
