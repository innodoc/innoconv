"""Unit tests for innoconv.runner"""

# pylint: disable=missing-docstring,too-many-instance-attributes

import unittest
from unittest.mock import call, DEFAULT, patch

from innoconv.extensions.abstract import AbstractExtension
from innoconv.manifest import Manifest
from innoconv.runner import InnoconvRunner

SHORT_MANIFEST = Manifest({
    'title': {
        'en': 'Foo Course Title',
        'de': 'Foo Kurstitel',
    },
    'languages': ('de', 'en')
})

MANIFEST = Manifest({
    'title': {
        'en': 'Foo Course Title',
        'de': 'Foo Kurstitel',
    },
    'languages': ('de', 'en'),
    'custom_content': ([{
        'name': 'about',
        'title_de': 'Über den Kurs',
        'title_en': 'About the course',
        'link_in_nav': True,
        'link_in_footer': True
    }])
})


def walk_side_effect(path):
    lang = path[-2:]
    return iter([
        (
            '/src/{}'.format(lang),
            ['section-1', 'section-2'],
            ['content.md'],
        ),
        (
            '/src/{}/section-1'.format(lang),
            ['section-1.1', 'section-1.2', '_static'],
            ['content.md'],
        ),
        (
            '/src/{}/section-1/section-1.1'.format(lang),
            [],
            ['content.md'],
        ),
        (
            '/src/{}/section-1/section-1.2'.format(lang),
            [],
            ['content.md'],
        ),
        (
            '/src/{}/section-2'.format(lang),
            [],
            ['content.md'],
        ),
    ])


def walk_side_effect_error(path):
    lang = path[-2:]
    return iter([
        (
            '/src/{}'.format(lang),
            ['section-1', 'section-2'],
            [],
        )
    ])


TITLE = [
    {
        't': 'Str',
        'c': 'Section',
    },
    {
        't': 'Space',
    },
    {
        't': 'Str',
        'c': 'title',
    },
]


@patch('builtins.open')
@patch('innoconv.runner.isfile', return_value=True)
@patch('innoconv.runner.to_ast', return_value=(['content_ast'], TITLE))
@patch('json.dump')
@patch('innoconv.runner.walk', side_effect=walk_side_effect)
@patch('innoconv.runner.makedirs')
@patch('innoconv.runner.isdir', return_value=True)
class TestInnoconvRunner(unittest.TestCase):
    def setUp(self):
        self.runner = InnoconvRunner('/src', '/out', MANIFEST, [])

    def test_run(self, *args):
        _, makedirs, _, json_dump, *_ = args
        self.runner.run()

        self.assertEqual(makedirs.call_count, 12)
        self.assertEqual(json_dump.call_count, 12)
        for i, path in enumerate((
                '/out/de',
                '/out/de/section-1',
                '/out/de/section-1/section-1.1',
                '/out/de/section-1/section-1.2',
                '/out/de/section-2',
                '/out/de/_content',
                '/out/en',
                '/out/en/section-1',
                '/out/en/section-1/section-1.1',
                '/out/en/section-1/section-1.2',
                '/out/en/section-2',
                '/out/en/_content',)):
            with self.subTest(path):
                self.assertEqual(
                    makedirs.call_args_list[i], call(path, exist_ok=True))
                self.assertEqual(
                    json_dump.call_args_list[i][0][0], ['content_ast'])

    def test_run_no_folder(self, isdir, *_):
        """Language folders do not exist"""
        isdir.return_value = False
        self.assertRaises(RuntimeError, self.runner.run)

    def test_run_no_custom_content_file(self, *args):
        """Custom content file does not exists"""
        _, _, _, _, _, is_file, *_ = args
        is_file.return_value = False
        self.assertRaises(RuntimeError, self.runner.run)

    def test_run_no_custom_content(self, *args):
        """There is no custom content"""
        _, makedirs, _, json_dump, *_ = args
        self.runner = InnoconvRunner('/src', '/out', SHORT_MANIFEST, [])
        self.runner.run()
        self.assertEqual(makedirs.call_count, 10)
        self.assertEqual(json_dump.call_count, 10)

    def test_run_content_file_missing(self, *args):
        _, _, walk, *_ = args
        walk.side_effect = walk_side_effect_error
        with self.assertRaises(RuntimeError):
            self.runner.run()

    def test_run_to_ast_fails(self, *args):
        _, _, _, _, to_ast, *_ = args
        to_ast.side_effect = RuntimeError()
        with self.assertRaises(RuntimeError):
            self.runner.run()


@patch('innoconv.runner.isfile', return_value=True)
@patch('builtins.open')
@patch('innoconv.runner.EXTENSIONS', {'my_ext': AbstractExtension})
@patch('innoconv.runner.to_ast', return_value=(['content_ast'], TITLE))
@patch('json.dump')
@patch('innoconv.runner.walk', side_effect=walk_side_effect)
@patch('innoconv.runner.makedirs')
@patch('innoconv.runner.isdir', return_value=True)
@patch('innoconv.extensions.abstract.AbstractExtension.__init__',
       return_value=None)
class TestInnoconvRunnerExtensions(unittest.TestCase):
    def test_valid_ext(self, init, *_):
        extensions = ('my_ext',)
        InnoconvRunner('/src', '/out', MANIFEST, extensions)
        self.assertIsInstance(init.call_args[0][0], Manifest)

    def test_invalid_ext(self, *_):
        extensions = ('my_ext', 'extension_does_not_exist')
        with self.assertRaises(RuntimeError):
            InnoconvRunner('/src', '/out', MANIFEST, extensions)

    @patch.multiple(
        'innoconv.extensions.abstract.AbstractExtension',
        start=DEFAULT,
        pre_conversion=DEFAULT,
        pre_process_file=DEFAULT,
        post_process_file=DEFAULT,
        post_conversion=DEFAULT,
        finish=DEFAULT,
    )
    def test_notify_ext(self, *_, **mocks):
        extensions = ('my_ext',)
        runner = InnoconvRunner('/src', '/out', MANIFEST, extensions)
        runner.run()

        self.assertEqual(mocks['start'].call_count, 1)
        self.assertEqual(mocks['start'].call_args, call('/out', '/src'))

        self.assertEqual(mocks['pre_conversion'].call_count, 2)
        self.assertEqual(mocks['pre_conversion'].call_args_list[0],
                         call('de'))
        self.assertEqual(mocks['pre_conversion'].call_args_list[1],
                         call('en'))

        self.assertEqual(mocks['pre_process_file'].call_count, 12)
        self.assertEqual(mocks['pre_process_file'].call_args_list[0],
                         call('de'))
        self.assertEqual(mocks['pre_process_file'].call_args_list[1],
                         call('de/section-1'))
        self.assertEqual(mocks['pre_process_file'].call_args_list[2],
                         call('de/section-1/section-1.1'))
        self.assertEqual(mocks['pre_process_file'].call_args_list[3],
                         call('de/section-1/section-1.2'))
        self.assertEqual(mocks['pre_process_file'].call_args_list[4],
                         call('de/section-2'))
        self.assertEqual(mocks['pre_process_file'].call_args_list[5],
                         call('de/_content'))
        self.assertEqual(mocks['pre_process_file'].call_args_list[6],
                         call('en'))
        self.assertEqual(mocks['pre_process_file'].call_args_list[7],
                         call('en/section-1'))
        self.assertEqual(mocks['pre_process_file'].call_args_list[8],
                         call('en/section-1/section-1.1'))
        self.assertEqual(mocks['pre_process_file'].call_args_list[9],
                         call('en/section-1/section-1.2'))
        self.assertEqual(mocks['pre_process_file'].call_args_list[10],
                         call('en/section-2'))
        self.assertEqual(mocks['pre_process_file'].call_args_list[11],
                         call('en/_content'))

        self.assertEqual(mocks['post_process_file'].call_count, 12)
        for i in range(0, 10):
            self.assertEqual(mocks['post_process_file'].call_args_list[i],
                             call(['content_ast'], TITLE))

        self.assertEqual(mocks['post_conversion'].call_count, 2)
        self.assertEqual(mocks['post_conversion'].call_args_list[0],
                         call('de'))
        self.assertEqual(mocks['post_conversion'].call_args_list[1],
                         call('en'))

        self.assertEqual(mocks['finish'].call_count, 1)
