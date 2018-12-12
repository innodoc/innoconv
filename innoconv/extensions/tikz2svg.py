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

With the image being the SVG rendered by the TikZ block:

.. image:: data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB3aWR0aD0iNDM2Ljc1MiIgaGVpZ2h0PSIzNi45ODciIHZpZXdCb3g9IjAgMCAzMjcuNTY0IDI3Ljc0Ij48ZGVmcz48c3ltYm9sIG92ZXJmbG93PSJ2aXNpYmxlIiBpZD0iYiI+PHBhdGggZD0iTTYuNTYzLTIuMjk3Yy4xNzEgMCAuMzU5IDAgLjM1OS0uMjAzIDAtLjE4OC0uMTg4LS4xODgtLjM2LS4xODhoLTUuMzljLS4xNzIgMC0uMzQ0IDAtLjM0NC4xODggMCAuMjAzLjE3Mi4yMDMuMzQ0LjIwM3ptMCAwIi8+PC9zeW1ib2w+PHN5bWJvbCBvdmVyZmxvdz0idmlzaWJsZSIgaWQ9ImMiPjxwYXRoIGQ9Ik00LjQ2OS0yYzAtMS4xODgtLjgxMy0yLjE4OC0xLjg5LTIuMTg4LS40NyAwLS45MDcuMTU3LTEuMjY3LjUxNnYtMS45NTNjLjIwNC4wNjMuNTMyLjEyNS44NDQuMTI1IDEuMjM1IDAgMS45MzgtLjkwNiAxLjkzOC0xLjAzMSAwLS4wNjMtLjAzMi0uMTEtLjExLS4xMSAwIDAtLjAzIDAtLjA3OC4wMzJhMy4yMiAzLjIyIDAgMCAxLTEuMzYuMjk2Yy0uMzkgMC0uODU4LS4wNzgtMS4zMjctLjI4LS4wNzgtLjAzMi0uMDk0LS4wMzItLjExLS4wMzJDMS02LjYyNSAxLTYuNTQ3IDEtNi4zOTF2Mi45NTRjMCAuMTcxIDAgLjI1LjE0LjI1LjA3OSAwIC4wOTQtLjAxNi4xNDEtLjA3OS4xMS0uMTU2LjQ2OS0uNzAzIDEuMjgyLS43MDMuNTE1IDAgLjc2NS40NTMuODQzLjY0LjE1Ni4zNzYuMTg4Ljc1LjE4OCAxLjI1IDAgLjM2IDAgLjk1NC0uMjUgMS4zNzYtLjIzNS4zOS0uNjEuNjQtMS4wNjMuNjQtLjcxOSAwLTEuMjk3LS41My0xLjQ2OS0xLjEwOS4wMzIgMCAuMDYzLjAxNi4xNzIuMDE2LjMyOSAwIC41LS4yNS41LS40ODUgMC0uMjUtLjE3MS0uNS0uNS0uNS0uMTQgMC0uNDg0LjA3OS0uNDg0LjUzMkMuNS0uNzUgMS4xODguMjE5IDIuMjk3LjIxOSAzLjQ1My4yMTkgNC40NjktLjczNCA0LjQ2OS0yem0wIDAiLz48L3N5bWJvbD48c3ltYm9sIG92ZXJmbG93PSJ2aXNpYmxlIiBpZD0iZCI+PHBhdGggZD0iTTIuOTM4LTEuNjR2Ljg1OWMwIC4zNi0uMDMyLjQ2OS0uNzY2LjQ2OWgtLjIwM1YwYy40MDYtLjAzMS45MjItLjAzMSAxLjM0My0uMDMxLjQyMiAwIC45MzggMCAxLjM2LjAzMXYtLjMxM2gtLjIxOWMtLjczNCAwLS43NS0uMTA5LS43NS0uNDY4di0uODZoLjk4NXYtLjMxMmgtLjk4NXYtNC41MzFjMC0uMjA0IDAtLjI2Ni0uMTcyLS4yNjYtLjA3OCAwLS4xMSAwLS4xODcuMTI1TC4yOC0xLjk1M3YuMzEyem0uMDQ2LS4zMTNILjU2M2wyLjQyMS0zLjcxOXptMCAwIi8+PC9zeW1ib2w+PHN5bWJvbCBvdmVyZmxvdz0idmlzaWJsZSIgaWQ9ImUiPjxwYXRoIGQ9Ik0yLjg5LTMuNTE2Yy44MTMtLjI2NSAxLjM5MS0uOTUzIDEuMzkxLTEuNzUgMC0uODEyLS44NzUtMS4zNzUtMS44MjgtMS4zNzUtMSAwLTEuNzY1LjU5NC0xLjc2NSAxLjM2IDAgLjMyOC4yMTguNTE1LjUxNS41MTUuMjk3IDAgLjUtLjIxOC41LS41MTUgMC0uNDg1LS40NjktLjQ4NS0uNjEtLjQ4NS4yOTgtLjUuOTU0LS42MjUgMS4zMTMtLjYyNS40MjIgMCAuOTY5LjIyLjk2OSAxLjExIDAgLjEyNS0uMDMxLjcwMy0uMjgxIDEuMTQtLjI5Ny40ODUtLjY0LjUxNi0uODkuNTE2YTMuMjkgMy4yOSAwIDAgMS0uMzkyLjAzMWMtLjA3OC4wMTYtLjE0LjAzMS0uMTQuMTI1IDAgLjExLjA2Mi4xMS4yMzQuMTFoLjQzOGMuODEyIDAgMS4xODcuNjcxIDEuMTg3IDEuNjU2IDAgMS4zNi0uNjg3IDEuNjQtMS4xMjUgMS42NC0uNDM3IDAtMS4xODctLjE3MS0xLjUzMS0uNzUuMzQ0LjA0Ny42NTYtLjE3MS42NTYtLjU0NmEuNTM3LjUzNyAwIDAgMC0uNTQ3LS41NjNjLS4yNSAwLS41NjIuMTQtLjU2Mi41NzhDLjQyMi0uNDM3IDEuMzQ0LjIyIDIuNDM3LjIyYzEuMjIgMCAyLjEyNi0uOTA2IDIuMTI2LTEuOTIyIDAtLjgxMy0uNjQxLTEuNTk0LTEuNjcyLTEuODEzem0wIDAiLz48L3N5bWJvbD48c3ltYm9sIG92ZXJmbG93PSJ2aXNpYmxlIiBpZD0iZiI+PHBhdGggZD0iTTEuMjY2LS43NjZsMS4wNjItMS4wM2MxLjU0Ny0xLjM3NiAyLjE0LTEuOTA3IDIuMTQtMi45MDcgMC0xLjE0LS44OS0xLjkzOC0yLjEwOS0xLjkzOEMxLjIzNC02LjY0LjUtNS43MTkuNS00LjgyOGMwIC41NDcuNS41NDcuNTMxLjU0Ny4xNzIgMCAuNTE2LS4xMS41MTYtLjUzMmEuNTEzLjUxMyAwIDAgMC0uNTMxLS41MTVjLS4wNzkgMC0uMDk0IDAtLjEyNS4wMTYuMjE4LS42NTcuNzY1LTEuMDE2IDEuMzQzLTEuMDE2LjkwNyAwIDEuMzI5LjgxMiAxLjMyOSAxLjYyNSAwIC43OTctLjQ4NSAxLjU3OC0xLjA0NyAyLjIwM0wuNjA5LS4zNzVDLjUtLjI2NS41LS4yMzUuNSAwaDMuNzAzbC4yNjYtMS43MzRoLS4yMzVDNC4xNzItMS40MzggNC4xMS0xIDQtLjg0NGMtLjA2My4wNzgtLjcxOS4wNzgtLjkzOC4wNzh6bTAgMCIvPjwvc3ltYm9sPjxzeW1ib2wgb3ZlcmZsb3c9InZpc2libGUiIGlkPSJnIj48cGF0aCBkPSJNMi45MzgtNi4zNzVjMC0uMjUgMC0uMjY2LS4yMzUtLjI2NkMyLjA3OC02IDEuMjAzLTYgLjg5MS02di4zMTNjLjIwMyAwIC43OCAwIDEuMjk2LS4yNjZ2NS4xNzJjMCAuMzYtLjAzLjQ2OS0uOTIxLjQ2OUguOTUzVjBjLjM0NC0uMDMxIDEuMjAzLS4wMzEgMS42MS0uMDMxLjM5IDAgMS4yNjUgMCAxLjYwOS4wMzF2LS4zMTNoLS4zMTNjLS45MDYgMC0uOTIxLS4xMDktLjkyMS0uNDY4em0wIDAiLz48L3N5bWJvbD48c3ltYm9sIG92ZXJmbG93PSJ2aXNpYmxlIiBpZD0iaCI+PHBhdGggZD0iTTQuNTc4LTMuMTg4YzAtLjc5Ni0uMDQ3LTEuNTkzLS4zOS0yLjMyOEMzLjczMy02LjQ4NCAyLjkwNS02LjY0IDIuNS02LjY0Yy0uNjEgMC0xLjMyOC4yNjYtMS43NSAxLjE4OC0uMzEzLjY4Ny0uMzYgMS40NjktLjM2IDIuMjY2IDAgLjc1LjAzMiAxLjY0LjQ1NCAyLjQwNmExLjgzIDEuODMgMCAwIDAgMS42NCAxYy41MzIgMCAxLjI5Ny0uMjAzIDEuNzM1LTEuMTU3LjMxMi0uNjg3LjM2LTEuNDY4LjM2LTIuMjV6TTIuNDg0IDBjLS4zOSAwLS45ODQtLjI1LTEuMTU2LTEuMjAzLS4xMS0uNTk0LS4xMS0xLjUxNi0uMTEtMi4xMSAwLS42NCAwLTEuMjk2LjA3OS0xLjgyOC4xODctMS4xODcuOTM3LTEuMjggMS4xODctMS4yOC4zMjkgMCAuOTg1LjE4NyAxLjE3MiAxLjE3MS4xMS41NjMuMTEgMS4zMTMuMTEgMS45MzggMCAuNzUgMCAxLjQyMS0uMTEgMi4wNjJDMy41LS4yOTcgMi45MzcgMCAyLjQ4NCAwem0wIDAiLz48L3N5bWJvbD48c3ltYm9sIG92ZXJmbG93PSJ2aXNpYmxlIiBpZD0iaSI+PHBhdGggZD0iTTEuMzEzLTMuMjY2di0uMjVjMC0yLjUxNSAxLjIzNC0yLjg3NSAxLjc1LTIuODc1LjIzNCAwIC42NTYuMDYzLjg3NC40MDctLjE1NiAwLS41NDYgMC0uNTQ2LjQzNyAwIC4zMTMuMjM0LjQ2OS40NTMuNDY5LjE1NiAwIC40NjktLjA5NC40NjktLjQ4NCAwLS41OTQtLjQzOC0xLjA3OS0xLjI2Ni0xLjA3OUMxLjc2Ni02LjY0LjQyMi01LjM1OS40MjItMy4xNTYuNDIyLS40ODQgMS41NzguMjE5IDIuNS4yMTljMS4xMSAwIDIuMDYzLS45MzggMi4wNjMtMi4yNSAwLTEuMjY2LS44OTEtMi4yMTktMi0yLjIxOS0uNjcyIDAtMS4wNDcuNS0xLjI1Ljk4NHpNMi41LS4wNjJjLS42MjUgMC0uOTIyLS41OTQtLjk4NC0uNzUtLjE4OC0uNDctLjE4OC0xLjI2Ni0uMTg4LTEuNDM4IDAtLjc4MS4zMjgtMS43ODEgMS4yMTktMS43ODEuMTcyIDAgLjYyNSAwIC45MzcuNjI1LjE3Mi4zNi4xNzIuODc1LjE3MiAxLjM2IDAgLjQ4MyAwIC45ODMtLjE3MiAxLjM0My0uMjk2LjU5NC0uNzUuNjQtLjk4NC42NHptMCAwIi8+PC9zeW1ib2w+PGNsaXBQYXRoIGlkPSJhIj48cGF0aCBkPSJNMyA1aDMyNC41NjN2Mkgzem0wIDAiLz48L2NsaXBQYXRoPjwvZGVmcz48ZyBjbGlwLXBhdGg9InVybCgjYSkiPjxwYXRoIGQ9Ik00LjAxNiA2LjE3NmgzMjMuMTUyIiBmaWxsPSJub25lIiBzdHJva2Utd2lkdGg9Ii43OTciIHN0cm9rZT0iIzAwMCIgc3Ryb2tlLW1pdGVybGltaXQ9IjEwIi8+PC9nPjxwYXRoIGQ9Ik05LjY4NC4ydjExLjk1NiIgZmlsbD0ibm9uZSIgc3Ryb2tlLXdpZHRoPSIuMzk5IiBzdHJva2U9IiMwMDAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIvPjx1c2UgeGxpbms6aHJlZj0iI2IiIHg9IjMuMzIxIiB5PSIyMy41ODkiLz48dXNlIHhsaW5rOmhyZWY9IiNjIiB4PSIxMS4wNjkiIHk9IjIzLjU4OSIvPjxwYXRoIGQ9Ik0zOC4wMzEuMnYxMS45NTYiIGZpbGw9Im5vbmUiIHN0cm9rZS13aWR0aD0iLjM5OSIgc3Ryb2tlPSIjMDAwIiBzdHJva2UtbWl0ZXJsaW1pdD0iMTAiLz48dXNlIHhsaW5rOmhyZWY9IiNiIiB4PSIzMS42NjciIHk9IjIzLjU4OSIvPjx1c2UgeGxpbms6aHJlZj0iI2QiIHg9IjM5LjQxNiIgeT0iMjMuNTg5Ii8+PHBhdGggZD0iTTY2LjM3OS4ydjExLjk1NiIgZmlsbD0ibm9uZSIgc3Ryb2tlLXdpZHRoPSIuMzk5IiBzdHJva2U9IiMwMDAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIvPjx1c2UgeGxpbms6aHJlZj0iI2IiIHg9IjYwLjAxMyIgeT0iMjMuNTg5Ii8+PHVzZSB4bGluazpocmVmPSIjZSIgeD0iNjcuNzYyIiB5PSIyMy41ODkiLz48cGF0aCBkPSJNOTQuNzIzLjJ2MTEuOTU2IiBmaWxsPSJub25lIiBzdHJva2Utd2lkdGg9Ii4zOTkiIHN0cm9rZT0iIzAwMCIgc3Ryb2tlLW1pdGVybGltaXQ9IjEwIi8+PHVzZSB4bGluazpocmVmPSIjYiIgeD0iODguMzYiIHk9IjIzLjU4OSIvPjx1c2UgeGxpbms6aHJlZj0iI2YiIHg9Ijk2LjEwOSIgeT0iMjMuNTg5Ii8+PHBhdGggZD0iTTEyMy4wNy4ydjExLjk1NiIgZmlsbD0ibm9uZSIgc3Ryb2tlLXdpZHRoPSIuMzk5IiBzdHJva2U9IiMwMDAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIvPjx1c2UgeGxpbms6aHJlZj0iI2IiIHg9IjExNi43MDYiIHk9IjIzLjU4OSIvPjx1c2UgeGxpbms6aHJlZj0iI2ciIHg9IjEyNC40NTUiIHk9IjIzLjU4OSIvPjxwYXRoIGQ9Ik0xNTEuNDE4LjJ2MTEuOTU2IiBmaWxsPSJub25lIiBzdHJva2Utd2lkdGg9Ii4zOTkiIHN0cm9rZT0iIzAwMCIgc3Ryb2tlLW1pdGVybGltaXQ9IjEwIi8+PHVzZSB4bGluazpocmVmPSIjaCIgeD0iMTQ4LjkyNyIgeT0iMjMuNTg5Ii8+PHBhdGggZD0iTTE3OS43NjYuMnYxMS45NTYiIGZpbGw9Im5vbmUiIHN0cm9rZS13aWR0aD0iLjM5OSIgc3Ryb2tlPSIjMDAwIiBzdHJva2UtbWl0ZXJsaW1pdD0iMTAiLz48dXNlIHhsaW5rOmhyZWY9IiNnIiB4PSIxNzcuMjc0IiB5PSIyMy41ODkiLz48cGF0aCBkPSJNMjA4LjExMy4ydjExLjk1NiIgZmlsbD0ibm9uZSIgc3Ryb2tlLXdpZHRoPSIuMzk5IiBzdHJva2U9IiMwMDAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIvPjx1c2UgeGxpbms6aHJlZj0iI2YiIHg9IjIwNS42MiIgeT0iMjMuNTg5Ii8+PHBhdGggZD0iTTIzNi40NTcuMnYxMS45NTYiIGZpbGw9Im5vbmUiIHN0cm9rZS13aWR0aD0iLjM5OSIgc3Ryb2tlPSIjMDAwIiBzdHJva2UtbWl0ZXJsaW1pdD0iMTAiLz48dXNlIHhsaW5rOmhyZWY9IiNlIiB4PSIyMzMuOTY2IiB5PSIyMy41ODkiLz48cGF0aCBkPSJNMjY0LjgwNS4ydjExLjk1NiIgZmlsbD0ibm9uZSIgc3Ryb2tlLXdpZHRoPSIuMzk5IiBzdHJva2U9IiMwMDAiIHN0cm9rZS1taXRlcmxpbWl0PSIxMCIvPjx1c2UgeGxpbms6aHJlZj0iI2QiIHg9IjI2Mi4zMTMiIHk9IjIzLjU4OSIvPjxwYXRoIGQ9Ik0yOTMuMTUyLjJ2MTEuOTU2IiBmaWxsPSJub25lIiBzdHJva2Utd2lkdGg9Ii4zOTkiIHN0cm9rZT0iIzAwMCIgc3Ryb2tlLW1pdGVybGltaXQ9IjEwIi8+PHVzZSB4bGluazpocmVmPSIjYyIgeD0iMjkwLjY1OSIgeT0iMjMuNTg5Ii8+PHBhdGggZD0iTTMyMS41LjJ2MTEuOTU2IiBmaWxsPSJub25lIiBzdHJva2Utd2lkdGg9Ii4zOTkiIHN0cm9rZT0iIzAwMCIgc3Ryb2tlLW1pdGVybGltaXQ9IjEwIi8+PHVzZSB4bGluazpocmVmPSIjaSIgeD0iMzE5LjAwNiIgeT0iMjMuNTg5Ii8+PC9zdmc+Cg==

"""  # noqa: E501


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
