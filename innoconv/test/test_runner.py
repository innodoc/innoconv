"""Unit tests for innoconv.runner"""

# pylint: disable=missing-docstring,too-many-instance-attributes

import unittest
import mock

from innoconv.extensions.abstract import AbstractExtension
from innoconv.manifest import Manifest
from innoconv.runner import InnoconvRunner

MANIFEST = Manifest({
    'title': {
        'en': 'Foo Course Title',
        'de': 'Foo Kurstitel',
    },
    'languages': ('de', 'en'),
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


@mock.patch('builtins.open')
@mock.patch('innoconv.runner.to_ast', return_value=(['content_ast'], TITLE))
@mock.patch('json.dump')
@mock.patch('innoconv.runner.walk', side_effect=walk_side_effect)
@mock.patch('innoconv.runner.makedirs')
@mock.patch('innoconv.runner.isdir', return_value=True)
class TestInnoconvRunner(unittest.TestCase):
    def setUp(self):
        self.runner = InnoconvRunner('/src', '/out', MANIFEST, [])

    def test_run(self, *args):
        _, makedirs, _, json_dump, *_ = args
        self.runner.run()

        self.assertEqual(makedirs.call_count, 10)
        self.assertEqual(json_dump.call_count, 10)
        for i, path in enumerate((
                '/out/de',
                '/out/de/section-1',
                '/out/de/section-1/section-1.1',
                '/out/de/section-1/section-1.2',
                '/out/de/section-2',
                '/out/en',
                '/out/en/section-1',
                '/out/en/section-1/section-1.1',
                '/out/en/section-1/section-1.2',
                '/out/en/section-2')):
            with self.subTest(path):
                self.assertEqual(
                    makedirs.call_args_list[i], mock.call(path, exist_ok=True))
                self.assertEqual(
                    json_dump.call_args_list[i][0][0], ['content_ast'])

    def test_run_no_folder(self, isdir, *_):
        """Language folders do not exist"""
        isdir.return_value = False
        self.assertRaises(RuntimeError, self.runner.run)

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


@mock.patch('builtins.open')
@mock.patch('innoconv.runner.EXTENSIONS', {'my_ext': AbstractExtension})
@mock.patch('innoconv.runner.to_ast', return_value=(['content_ast'], TITLE))
@mock.patch('json.dump')
@mock.patch('innoconv.runner.walk', side_effect=walk_side_effect)
@mock.patch('innoconv.runner.makedirs')
@mock.patch('innoconv.runner.isdir', return_value=True)
@mock.patch('innoconv.extensions.abstract.AbstractExtension.__init__',
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

    @mock.patch.multiple(
        'innoconv.extensions.abstract.AbstractExtension',
        start=mock.DEFAULT,
        pre_conversion=mock.DEFAULT,
        pre_process_file=mock.DEFAULT,
        post_process_file=mock.DEFAULT,
        post_conversion=mock.DEFAULT,
        finish=mock.DEFAULT,
    )
    def test_notify_ext(self, *_, **mocks):
        extensions = ('my_ext',)
        runner = InnoconvRunner('/src', '/out', MANIFEST, extensions)
        runner.run()

        self.assertEqual(mocks['start'].call_count, 1)
        self.assertEqual(mocks['start'].call_args, mock.call('/out', '/src'))

        self.assertEqual(mocks['pre_conversion'].call_count, 2)
        self.assertEqual(mocks['pre_conversion'].call_args_list[0],
                         mock.call('de'))
        self.assertEqual(mocks['pre_conversion'].call_args_list[1],
                         mock.call('en'))

        self.assertEqual(mocks['pre_process_file'].call_count, 10)
        self.assertEqual(mocks['pre_process_file'].call_args_list[0],
                         mock.call('de'))
        self.assertEqual(mocks['pre_process_file'].call_args_list[1],
                         mock.call('de/section-1'))
        self.assertEqual(mocks['pre_process_file'].call_args_list[2],
                         mock.call('de/section-1/section-1.1'))
        self.assertEqual(mocks['pre_process_file'].call_args_list[3],
                         mock.call('de/section-1/section-1.2'))
        self.assertEqual(mocks['pre_process_file'].call_args_list[4],
                         mock.call('de/section-2'))
        self.assertEqual(mocks['pre_process_file'].call_args_list[5],
                         mock.call('en'))
        self.assertEqual(mocks['pre_process_file'].call_args_list[6],
                         mock.call('en/section-1'))
        self.assertEqual(mocks['pre_process_file'].call_args_list[7],
                         mock.call('en/section-1/section-1.1'))
        self.assertEqual(mocks['pre_process_file'].call_args_list[8],
                         mock.call('en/section-1/section-1.2'))
        self.assertEqual(mocks['pre_process_file'].call_args_list[9],
                         mock.call('en/section-2'))

        self.assertEqual(mocks['post_process_file'].call_count, 10)
        for i in range(0, 10):
            self.assertEqual(mocks['post_process_file'].call_args_list[i],
                             mock.call(['content_ast'], TITLE))

        self.assertEqual(mocks['post_conversion'].call_count, 2)
        self.assertEqual(mocks['post_conversion'].call_args_list[0],
                         mock.call('de'))
        self.assertEqual(mocks['post_conversion'].call_args_list[1],
                         mock.call('en'))

        self.assertEqual(mocks['finish'].call_count, 1)
