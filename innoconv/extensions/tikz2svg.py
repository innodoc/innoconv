r"""
Convert and insert Ti\ *k*\Z figures.

SVG files are be rendered from Ti\ *k*\Z code and saved in the folder ``_tikz``
in the static folder of the output directory.

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


from hashlib import md5
from logging import critical, info
from os import mkdir
from os.path import join
from shutil import copytree, rmtree
from subprocess import PIPE, Popen
from tempfile import TemporaryDirectory

from innoconv.constants import ENCODING, STATIC_FOLDER
from innoconv.extensions.abstract import AbstractExtension

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
        super(Tikz2Svg, self).__init__(*args, **kwargs)
        self._output_dir = None
        self._tikz_images = None

    @staticmethod
    def _run(cmd, cwd, stdin=None):
        pipe = Popen(
            cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, cwd=cwd
        )
        if stdin:
            pipe.stdin.write(stdin.encode(ENCODING))
            pipe.stdin.close()
        pipe.wait()
        if pipe.returncode != 0:
            critical(cmd)
            critical("Error: {}".format(pipe.returncode))
            critical("Printing program output for debugging:")
            critical(pipe.stdout.read().decode(ENCODING))
            if stdin:
                critical("Printing STDIN:")
                critical(stdin)
            raise RuntimeError("Tikz2Pdf: Error converting to PDF!")

    @staticmethod
    def _get_tikz_name(tikz_hash):
        return TIKZ_FILENAME.format(tikz_hash)

    def _tikz_found(self, element, caption=None):
        """Remember TikZ code and replace with image."""
        code = element["c"][1].strip()
        tikz_hash = md5(code.encode()).hexdigest()
        self._tikz_images[tikz_hash] = code
        filename = "{}.svg".format(Tikz2Svg._get_tikz_name(tikz_hash))
        element["t"] = "Image"
        element["c"] = [
            ["", [], []],
            caption or [],
            [join(TIKZ_FOLDER, filename), TIKZ_IMG_TAG_ALT],
        ]
        info("Found TikZ image {}".format(filename))

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

    def _process_ast_element(self, elem, parent=None):
        """Process an element form the AST and traverse its children."""

        if isinstance(elem, list):
            for child in elem:
                self._process_ast_element(child, parent)
            return
        try:
            try:
                if elem["t"] == "CodeBlock" and "tikz" in elem["c"][0][1]:
                    self._parse_tikz(elem, parent)
            except (TypeError, KeyError):
                pass
            for key in elem:
                self._process_ast_element(elem[key], elem)
        except TypeError:
            pass

    def _render_and_copy_tikz(self):
        info("Compiling {} TikZ images.".format(len(self._tikz_images)))
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
                info("Compiling {}".format(file_base))
                # compile tex
                cmd = CMD_PDFLATEX.format(join("pdf_out", file_base))
                self._run(cmd, tmp_dir, stdin=texdoc)
                # convert to SVG
                pdf_filename = join(pdf_path, "{}.pdf".format(file_base))
                svg_filename = join(svg_path, "{}.svg".format(file_base))
                cmd = CMD_PDF2SVG.format(pdf_filename, svg_filename)
                self._run(cmd, tmp_dir)
            # copy SVG files
            tikz_path = join(self._output_dir, STATIC_FOLDER, TIKZ_FOLDER)
            try:
                copytree(svg_path, tikz_path)
            except FileExistsError:
                rmtree(tikz_path)
                copytree(svg_path, tikz_path)

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