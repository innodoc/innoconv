"""Unit tests for innoconv.runner"""

# pylint: disable=missing-docstring,too-many-instance-attributes

import unittest
import mock

from innoconv.runner import InnoconvRunner


def walk_side_effect(path):
    lang = path[-2:]
    return iter([
        (
            '/source_dir/{}'.format(lang),
            ['section-1', 'section-2'],
            ['content.md'],
        ),
        (
            '/source_dir/{}/section-1'.format(lang),
            ['section-1.1', 'section-1.2'],
            ['content.md'],
        ),
        (
            '/source_dir/{}/section-1/section-1.1'.format(lang),
            [],
            ['content.md'],
        ),
        (
            '/source_dir/{}/section-1/section-1.2'.format(lang),
            [],
            ['content.md'],
        ),
        (
            '/source_dir/{}/section-2'.format(lang),
            [],
            ['content.md'],
        ),
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


class TestInnoconvRunner(unittest.TestCase):

    def setUp(self):
        runner_to_ast_patcher = mock.patch('innoconv.runner.to_ast')
        self.runner_to_ast_mock = runner_to_ast_patcher.start()
        self.runner_to_ast_mock.return_value = ['content_ast'], TITLE

        json_dump_patcher = mock.patch('json.dump')
        self.json_dump_mock = json_dump_patcher.start()

        builtins_open_patcher = mock.patch('builtins.open')
        self.builtins_open_mock = builtins_open_patcher.start()

        os_walk_patcher = mock.patch('innoconv.runner.walk')
        self.os_walk_mock = os_walk_patcher.start()
        self.os_walk_mock.side_effect = walk_side_effect

        os_makedirs_patcher = mock.patch('innoconv.runner.makedirs')
        self.os_makedirs_mock = os_makedirs_patcher.start()

        os_path_isdir_patcher = mock.patch('innoconv.runner.isdir')
        self.os_path_isdir_mock = os_path_isdir_patcher.start()
        self.os_path_isdir_mock.return_value = True

        self.addCleanup(mock.patch.stopall)

        self.runner = InnoconvRunner(
            '/source_dir', '/output_dir', ['de', 'en'])

    def test_run(self):
        self.runner.run()

        self.assertEqual(self.os_makedirs_mock.call_count, 10)
        for i, path in enumerate((
                '/output_dir/de',
                '/output_dir/de/section-1',
                '/output_dir/de/section-1/section-1.1',
                '/output_dir/de/section-1/section-1.2',
                '/output_dir/de/section-2',
                '/output_dir/en',
                '/output_dir/en/section-1',
                '/output_dir/en/section-1/section-1.1',
                '/output_dir/en/section-1/section-1.2',
                '/output_dir/en/section-2')):
            args, _ = self.os_makedirs_mock.call_args_list[i]
            self.assertEqual(args[0], path)

        # called 10 times for content files
        self.assertEqual(self.json_dump_mock.call_count, 12)
        for i in (0, 1, 2, 3, 4, 6, 7, 8, 9, 10):
            args, _ = self.json_dump_mock.call_args_list[i]
            self.assertEqual(args[0], ['content_ast'])

        # called twice for TOCs
        for i in (5, 11):
            toc = self.json_dump_mock.call_args_list[i][0][0]
            self.assertEqual(toc, [
                {
                    'id': 'section-1',
                    'title': TITLE,
                    'children': [
                        {
                            'id': 'section-1.1',
                            'title': TITLE,
                        },
                        {
                            'id': 'section-1.2',
                            'title': TITLE,
                        },
                    ],
                },
                {
                    'id': 'section-2',
                    'title': TITLE,
                },
            ])

    def test_run_no_folder(self):
        """Language folders do not exist"""
        self.os_path_isdir_mock.return_value = False
        self.assertRaises(RuntimeError, self.runner.run)
