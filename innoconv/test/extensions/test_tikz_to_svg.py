"""Unit tests for tikz2svg extension"""

# pylint: disable=missing-docstring

import copy
import os
import mock

from innoconv.extensions.tikz2svg import Tikz2Svg, run
from innoconv.constants import STATIC_FOLDER, TIKZ_FOLDER, TIKZ_FILENAME
from innoconv.constants import ENCODING
from innoconv.test.utils import get_tricky_ast_parts, get_manifest
from innoconv.test.utils import get_image_ast
from innoconv.test.extensions import TestExtension, DEST, TEMP

TIKZSTRING = ("\\begin{tikzpicture}[x=1.0cm, y=1.0cm] \n"
              "\\draw[thick, black] (-5.2,0) -- (6.2,0);\n"
              "\\foreach \\x in {-5, -4, ..., 6}\n"
              "\\draw[shift={(\\x,0)},color=black] (0pt,6pt) -- (0pt,-6pt) "
              "node[below=1.5pt] {\\normalsize $\\x$};\n"
              "\\end{tikzpicture}\n")

TIKZBLOCK = {
    "t": "CodeBlock",
    "c": [
        [
            "",
            ["tikz"],
            []
        ],
        TIKZSTRING
    ]
}

IMAGEBLOCK = get_image_ast(
    '/'+os.path.join(TIKZ_FOLDER, TIKZ_FILENAME.format(0)),
    description='TikZ Image')

PATHS = (
    ("Foo", ('foo',)),
)


class TestTikz2Svg(TestExtension):

    def __init__(self, arg):
        super(TestTikz2Svg, self).__init__(arg)
        self.tikz2svg = Tikz2Svg(get_manifest())

    @staticmethod
    def _run(extension=None, ast=None, languages=('de',), paths=PATHS):
        return TestExtension._run(
            Tikz2Svg, ast, paths=PATHS, languages=languages)

    @mock.patch('innoconv.extensions.tikz2svg.Popen')
    def test_run(self, mock_popen):
        test_cmd = "x_call_x"
        input_value = 'x_input_x'
        output_value = 'x_output_x'
        mock_popen.return_value.stdout.read.return_value = output_value.encode(
            ENCODING)
        mock_popen.return_value.returncode = 0

        with self.subTest(stdin=None):
            self.assertEqual(output_value, run(test_cmd))
            self.assertTrue(mock_popen.called)
            mock_popen.reset_mock()

        with self.subTest(stdin=input_value):
            self.assertEqual(output_value, run(test_cmd, input_value))
            mock_popen.return_value.stdin.write.assert_called_with(
                input_value.encode(ENCODING))

    @mock.patch('innoconv.extensions.tikz2svg.Popen')
    @mock.patch('innoconv.extensions.tikz2svg.critical')
    def test_run_error(self, mock_critical, mock_popen):
        test_cmd = "x_call_x"
        error_value = 'x_error_x'
        mock_popen.return_value.stderr.read.return_value = error_value.encode(
            ENCODING)

        mock_popen.return_value.returncode = 1
        with self.assertRaises(RuntimeError):
            run(test_cmd)
        mock_critical.assert_has_calls([
            mock.call(test_cmd),
            mock.call('Error: %i', 1),
            mock.call(error_value)
        ])

    def test_replace_block(self):
        self.tikz2svg.tikz_images = list()
        block = copy.deepcopy(TIKZBLOCK)
        self.tikz2svg.replace_tikz_element(block)
        self.assertEqual(block, IMAGEBLOCK)
        self.assertIn(TIKZSTRING, self.tikz2svg.tikz_images)

    def test_tricky_ast(self):
        for test in get_tricky_ast_parts():
            with self.subTest(test=test):
                self.tikz2svg.post_process_file(test, None)

    @mock.patch("builtins.open", new_callable=mock.mock_open, read_data="data")
    @mock.patch('innoconv.extensions.tikz2svg.copy_tree')
    @mock.patch('innoconv.extensions.tikz2svg.mkdir')
    @mock.patch('innoconv.extensions.tikz2svg.run')
    def test_conversion(self, mock_run, mock_mkdir, mock_copy_tree, mock_open):
        self.tikz2svg.tikz_images = list()
        self.tikz2svg.tikz_images.append(TIKZSTRING)
        self.tikz2svg.output_dir_base = DEST
        self.tikz2svg.create_files(TEMP)

        tex_file_path = os.path.join(TEMP, 'input.tex')
        mock_open.assert_called_with(tex_file_path, 'w+')
        self.assertIn(TIKZSTRING, mock_open.return_value.write.call_args[0][0])

        self.assertEqual(mock_run.call_count, 2)
        for args in mock_run.call_args_list:
            command = args[0][0]
            if command.startswith("pdf2svg"):
                self.assertIn(TIKZ_FILENAME.format(0), command)
            else:
                self.assertTrue(command.startswith("pdflatex"))

        svgs_path = os.path.join(TEMP, 'svgs')
        ouput_path = os.path.join(DEST, STATIC_FOLDER, TIKZ_FOLDER)
        mock_mkdir.assert_called_with(svgs_path)
        mock_copy_tree.assert_called_with(svgs_path, ouput_path, update=1)

    @mock.patch('innoconv.extensions.tikz2svg.Tikz2Svg.create_files')
    @mock.patch('innoconv.extensions.tikz2svg.getcwd')
    @mock.patch('innoconv.extensions.tikz2svg.chdir')
    @mock.patch('innoconv.extensions.tikz2svg.TemporaryDirectory')
    def test_simple_life_cycle(self, mock_temporary_directory, mock_chdir,
                               mock_getcwd, mock_create_files):
        block = copy.deepcopy(TIKZBLOCK)
        current_dir = 'x_path_x'
        temp_dir = 'x_path_temp_x'

        mock_temporary_directory.return_value.__enter__.return_value = (
            temp_dir)
        mock_getcwd.return_value = current_dir

        tikz2svg = self._run(ast=[{'c': [block]}])

        self.assertTrue(mock_getcwd.called)
        self.assertTrue(mock_temporary_directory.called)
        mock_chdir.assert_has_calls([
            mock.call(temp_dir),
            mock.call(current_dir)
        ])
        mock_create_files.assert_called_with(temp_dir)
        self.assertEqual(IMAGEBLOCK, block)
        self.assertEqual(tikz2svg.output_dir_base, DEST)
