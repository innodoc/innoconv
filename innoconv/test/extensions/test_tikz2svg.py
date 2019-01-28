"""Unit tests for tikz2svg extension"""

# pylint: disable=missing-docstring
# pylint: disable=W0212

import copy
import os
from hashlib import md5
import mock

from innoconv.extensions.tikz2svg import Tikz2Svg, _get_tikz_name
from innoconv.constants import STATIC_FOLDER, TIKZ_FOLDER
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

TIKZHASH = md5(TIKZSTRING.strip().encode()).hexdigest()

IMAGEBLOCK = get_image_ast(
    os.path.join(TIKZ_FOLDER, _get_tikz_name(TIKZHASH)) + '.svg',
    description='TikZ Image')

PATHS = (
    ("Foo", ('foo',)),
)


class TestTikz2Svg(TestExtension):
    def __init__(self, arg):
        super(TestTikz2Svg, self).__init__(arg)
        self.tikz2svg = Tikz2Svg(get_manifest())

    @staticmethod
    def _run(extension=None, ast=None, languages=('de',), paths=PATHS,
             manifest=None):
        return TestExtension._run(
            Tikz2Svg, ast, paths=PATHS, languages=languages, manifest=manifest)

    def test_popen(self):
        self.tikz2svg._run("which pdflatex", "/")
        self.tikz2svg._run("pdflatex --version", "/")

    @mock.patch('innoconv.extensions.tikz2svg.Popen')
    def test_run(self, mock_popen):
        test_cmd = "x_call_x"
        test_value = 'x_test_x'
        process_mock = mock.Mock()
        mock_popen.return_value = process_mock
        process_mock.returncode = 0
        Tikz2Svg._run(test_cmd, "", test_value)
        process_mock.stdin.write.assert_called_with(test_value.encode(
            ENCODING))
        self.assertTrue(process_mock.stdin.close.called)
        self.assertTrue(process_mock.wait.called)

    @mock.patch('innoconv.extensions.tikz2svg.Popen')
    @mock.patch('innoconv.extensions.tikz2svg.critical')
    def test_run_error(self, mock_critical, mock_popen):
        test_cmd = "x_call_x"
        error_value = 'x_error_x'
        stdin_value = 'x_stdin_x'
        mock_popen.return_value.stdout.read.return_value = error_value.encode(
            ENCODING)
        mock_popen.return_value.returncode = 1
        with self.assertRaises(RuntimeError):
            Tikz2Svg._run(test_cmd, "")
        mock_critical.assert_has_calls([
            mock.call(test_cmd),
            mock.call('Error: 1'),
            mock.call('Printing program output for debugging:'),
            mock.call(error_value)
        ])
        mock_critical.reset()
        with self.assertRaises(RuntimeError):
            Tikz2Svg._run(test_cmd, "", stdin=stdin_value)
        mock_critical.assert_has_calls([
            mock.call(test_cmd),
            mock.call('Error: 1'),
            mock.call('Printing program output for debugging:'),
            mock.call(error_value),
            mock.call('Printing STDIN:'),
            mock.call(stdin_value),
        ])

    def test_replace_block(self):
        self.tikz2svg._tikz_images = dict()
        block = copy.deepcopy(TIKZBLOCK)
        self.tikz2svg.post_process_file(block, None)
        self.assertEqual(block, IMAGEBLOCK)
        self.assertIn(TIKZHASH, self.tikz2svg._tikz_images)

    def test_tricky_ast(self):
        for test in get_tricky_ast_parts():
            with self.subTest(test=test):
                self.tikz2svg.post_process_file(test, None)

    @mock.patch("builtins.open", new_callable=mock.mock_open, read_data="data")
    @mock.patch('innoconv.extensions.tikz2svg.copy_tree')
    @mock.patch('innoconv.extensions.tikz2svg.mkdir')
    @mock.patch('innoconv.extensions.tikz2svg.Tikz2Svg._run')
    @mock.patch('innoconv.extensions.tikz2svg.TemporaryDirectory')
    def test_conversion(self, mock_temporary_directory, mock_run, mock_mkdir,
                        mock_copy_tree, _):
        mock_temporary_directory.return_value.__enter__.return_value = TEMP
        self.tikz2svg._tikz_images = dict()
        self.tikz2svg._tikz_images[TIKZHASH] = TIKZSTRING
        self.tikz2svg._output_dir = DEST
        self.tikz2svg.finish()
        self.assertEqual(mock_run.call_count, 2)
        for args in mock_run.call_args_list:
            command = args[0][0]
            if command.startswith("pdf2svg"):
                self.assertIn(_get_tikz_name(TIKZHASH), command)
            else:
                self.assertTrue(command.startswith("pdflatex"))
        svgs_path = os.path.join(TEMP, 'svg_out')
        ouput_path = os.path.join(DEST, STATIC_FOLDER, TIKZ_FOLDER)
        mock_mkdir.assert_called_with(svgs_path)
        mock_copy_tree.assert_called_with(svgs_path, ouput_path, update=1)

    @mock.patch('innoconv.extensions.tikz2svg.Tikz2Svg._run')
    @mock.patch('innoconv.extensions.tikz2svg.TemporaryDirectory')
    @mock.patch('innoconv.extensions.tikz2svg.copy_tree')
    @mock.patch('innoconv.extensions.tikz2svg.mkdir')
    def test_simple_life_cycle(self, mock_mkdir, mock_copy_tree,
                               mock_temporary_directory, _):
        block = copy.deepcopy(TIKZBLOCK)
        mock_temporary_directory.return_value.__enter__.return_value = ''
        tikz2svg, asts = self._run(ast=[{'c': [block]}])
        self.assertTrue(mock_temporary_directory.called)
        self.assertTrue(mock_copy_tree.called)
        self.assertTrue(mock_mkdir.called)
        block = asts[0][0]['c'][0]
        self.assertEqual(IMAGEBLOCK, block)
        self.assertEqual(tikz2svg._output_dir, DEST)

    @mock.patch('innoconv.extensions.tikz2svg.Tikz2Svg._run')
    @mock.patch('innoconv.extensions.tikz2svg.TemporaryDirectory')
    @mock.patch('innoconv.extensions.tikz2svg.copy_tree')
    @mock.patch('innoconv.extensions.tikz2svg.mkdir')
    def test_empty_life_cycle(self, mock_mkdir, mock_copy_tree,
                              mock_temporary_directory, _):
        mock_temporary_directory.return_value.__enter__.return_value = ''
        tikz2svg, asts = self._run(ast=[])
        self.assertFalse(mock_temporary_directory.called)
        self.assertFalse(mock_copy_tree.called)
        self.assertFalse(mock_mkdir.called)
        self.assertEqual(0, len(asts[0]))
        self.assertEqual(tikz2svg._output_dir, DEST)

    @mock.patch('innoconv.extensions.tikz2svg.Tikz2Svg._run')
    @mock.patch('innoconv.extensions.tikz2svg.TemporaryDirectory')
    @mock.patch('innoconv.extensions.tikz2svg.copy_tree')
    @mock.patch('innoconv.extensions.tikz2svg.mkdir')
    def test_with_caption(self, mock_mkdir, mock_copy_tree,
                          mock_temporary_directory, _):
        block = copy.deepcopy(TIKZBLOCK)
        content = [
            {'t': 'Div',
             'c': [
                 [None, ['figure'], None],
                 [{'t': 'Para',
                   'c': [{'c': 'x_caption_x', 't': 'Str'}]}],
                 block
             ]}
        ]
        mock_temporary_directory.return_value.__enter__.return_value = ''
        tikz2svg, asts = self._run(ast=[{'c': [content]}])
        self.assertTrue(mock_temporary_directory.called)
        self.assertTrue(mock_copy_tree.called)
        self.assertTrue(mock_mkdir.called)
        block = asts[0][0]['c'][0][0]['c'][2]
        image_block = copy.deepcopy(IMAGEBLOCK)
        image_block['c'][1].append({'c': 'x_caption_x', 't': 'Str'})
        self.assertEqual(image_block, block)
        self.assertEqual(tikz2svg._output_dir, DEST)

    @mock.patch('innoconv.extensions.tikz2svg.Tikz2Svg._run')
    @mock.patch('innoconv.extensions.tikz2svg.TemporaryDirectory')
    @mock.patch('innoconv.extensions.tikz2svg.copy_tree')
    @mock.patch('innoconv.extensions.tikz2svg.mkdir')
    def test_preamble(self, mock_mkdir, mock_copy_tree,
                      mock_temporary_directory, mock_run):
        block = copy.deepcopy(TIKZBLOCK)
        mock_temporary_directory.return_value.__enter__.return_value = ''
        tikz2svg, asts = self._run(ast=[{'c': [block]}], manifest={
            'tikz_preamble': 'x_tikz_preamble_x'})
        self.assertTrue(mock_temporary_directory.called)
        self.assertTrue(mock_copy_tree.called)
        self.assertTrue(mock_mkdir.called)
        block = asts[0][0]['c'][0]
        self.assertEqual(IMAGEBLOCK, block)
        self.assertEqual(tikz2svg._output_dir, DEST)
        self.assertIn('x_tikz_preamble_x',
                      mock_run.call_args_list[0][1]['stdin'])
