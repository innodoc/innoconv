"""Unit tests for CopyStatic."""

# pylint: disable=missing-docstring

from os.path import join
import itertools
import mock

from innoconv.extensions.copy_static import CopyStatic
from innoconv.constants import STATIC_FOLDER
from innoconv.test.utils import (
    get_filler_content, get_image_ast, get_video_ast, get_generic_link_ast,
    get_para_ast, get_youtube_ast)
from innoconv.test.extensions import SOURCE, TARGET, PATHS, TestExtension


@mock.patch('os.makedirs', return_value=True)
@mock.patch('os.path.lexists', return_value=True)
@mock.patch('os.path.isfile', side_effect=itertools.cycle((True,)))
@mock.patch('shutil.copyfile')
class TestCopyStatic(TestExtension):
    def test_absolute_localized(self, copyfile, *_):
        self._run(
            CopyStatic, [get_image_ast('/present.jpg')], languages=('en',))
        self.assertEqual(copyfile.call_count, 1)
        src = join(SOURCE, 'en', STATIC_FOLDER, 'present.jpg')
        target = join(TARGET, 'en', STATIC_FOLDER, 'present.jpg')
        self.assertEqual(mock.call(src, target), copyfile.call_args)

    def test_absolute_nonlocalized(self, copyfile, isfile, *_):
        isfile.side_effect = itertools.cycle((False, True))
        self._run(
            CopyStatic, [get_image_ast('/present.jpg')], languages=('en',))
        self.assertEqual(copyfile.call_count, 1)
        src = join(SOURCE, STATIC_FOLDER, 'present.jpg')
        target = join(TARGET, STATIC_FOLDER, 'present.jpg')
        self.assertEqual(mock.call(src, target), copyfile.call_args)

    def test_example(self, copyfile, *_):
        ast = [
            get_para_ast(),
            get_para_ast([get_image_ast('/present.png', 'Image Present')]),
            get_para_ast(
                [get_para_ast([get_image_ast('/subfolder/present.mp4')])]),
            get_para_ast([
                get_para_ast(get_para_ast()),
                get_para_ast([get_filler_content()]),
                get_image_ast('/localizable.gif', '', 'Description!'),
                get_image_ast('example_video.ogv')
            ]),
            get_image_ast('https://www.example.com/example.png'),
            get_para_ast([
                get_generic_link_ast(
                    [get_image_ast('example_image.jpg')],
                    'http://www.tu-berlin.de')
            ]),
        ]
        self._run(CopyStatic, ast, languages=('en',))
        self.assertEqual(copyfile.call_count, 11)

    def test_file_does_not_exist(self, *args):
        _, isfile, _, _ = args
        isfile.side_effect = itertools.cycle((False, ))
        tests = (
            ('/not-present.png', [get_image_ast('/not-present.png')]),
            ('/not-present.mp4', [get_video_ast('/not-present.mp4')]),
            ('/single_language.svg', [get_image_ast('/single_language.svg')]),
        )
        for name, ast in tests:
            with self.subTest(name):
                with self.assertRaises(RuntimeError):
                    self._run(CopyStatic, ast)

    def test_ignore_remote(self, copyfile, *_):
        tests = (
            'http://www.example.com/example.png',
            'http://www.example.com/example.png',
            'ftp://ftp.example.com/example.png',
        )
        for addr in tests:
            with self.subTest(addr):
                self._run(CopyStatic, [get_image_ast(addr)])
                self.assertEqual(copyfile.call_count, 0)

    def test_ignore_remote_static(self, copyfile, *_):
        self._run(
            CopyStatic, [get_video_ast('https://www.example.com/video.ogv')])
        self.assertEqual(copyfile.call_count, 0)

    def test_ignore_youtube(self, copyfile, *_):
        ast = [get_youtube_ast(
            'https://www.youtube.com/watch?v=C0DPdy98e4c', title='Test video')]
        self._run(CopyStatic, ast)
        self.assertEqual(copyfile.call_count, 0)

    def test_linked_picture(self, copyfile, *_):
        ast = [get_generic_link_ast(
            [get_image_ast('/present.png')],
            'http://www.tu-berlin.de')]
        self._run(CopyStatic, ast, languages=('en',))
        self.assertEqual(copyfile.call_count, 1)

    def test_make_target_dirs(self, *args):
        _, _, lexists, makedirs = args
        lexists.return_value = False
        ast = [get_image_ast('test.png')]
        self._run(CopyStatic, ast, languages=('en',))
        self.assertEqual(makedirs.call_count, 4)
        for _, path in PATHS:
            call = mock.call(join(TARGET, 'en', STATIC_FOLDER, *path))
            with self.subTest(call):
                self.assertIn(call, makedirs.call_args_list)

    def test_only_en_present(self, copyfile, isfile, *_):
        ast = [get_image_ast('localizable.gif')]
        languages = ('en', 'la')
        isfile.side_effect = lambda p: '/la/' not in p
        self._run(CopyStatic, ast, languages=languages)
        self.assertEqual(copyfile.call_count, 8)
        for lang_path in (('en',), ()):
            src_base = join(SOURCE, *lang_path, STATIC_FOLDER)
            target_base = join(TARGET, *lang_path, STATIC_FOLDER)
            for _, path in PATHS:
                src = join(src_base, *path, 'localizable.gif')
                target = join(target_base, *path, 'localizable.gif')
                call = mock.call(src, target)
                with self.subTest(call):
                    self.assertIn(call, copyfile.call_args_list)

    def test_relative_localized(self, copyfile, *_):
        ast = [get_video_ast('example_video.ogv')]
        self._run(CopyStatic, ast, languages=('en',))
        self.assertEqual(copyfile.call_count, 4)
        for _, path in PATHS:
            src = join(
                SOURCE, 'en', STATIC_FOLDER, *path, 'example_video.ogv')
            target = join(
                TARGET, 'en', STATIC_FOLDER, *path, 'example_video.ogv')
            call = mock.call(src, target)
            with self.subTest(call):
                self.assertIn(call, copyfile.call_args_list)

    def test_relative_nonlocalized(self, copyfile, isfile, *_):
        isfile.side_effect = itertools.cycle((False, True))
        ast = [get_image_ast('example_image.jpg')]
        self._run(CopyStatic, ast, languages=('en',))
        self.assertEqual(copyfile.call_count, 4)
        for _, path in PATHS:
            src = join(SOURCE, STATIC_FOLDER, *path, 'example_image.jpg')
            target = join(TARGET, STATIC_FOLDER, *path, 'example_image.jpg')
            call = mock.call(src, target)
            with self.subTest(call):
                self.assertIn(call, copyfile.call_args_list)

    def test_relative_two_langs(self, copyfile, *_):
        languages = ('de', 'en')
        ast = [get_image_ast('localized_present.png')]
        self._run(CopyStatic, ast, languages=languages)
        self.assertEqual(copyfile.call_count, 8)
        for _, path in PATHS:
            for lang in languages:
                src = join(
                    SOURCE, lang, STATIC_FOLDER, *path,
                    'localized_present.png')
                target = join(
                    TARGET, lang, STATIC_FOLDER, *path,
                    'localized_present.png')
                call = mock.call(src, target)
                self.assertIn(call, copyfile.call_args_list)

    def test_stacked_single_picture(self, copyfile, *_):
        ast = [
            get_para_ast(),
            get_para_ast([get_image_ast('/present.png')]),
            get_para_ast([[get_para_ast()]]),
            get_para_ast([get_para_ast([get_para_ast()]), get_para_ast()])
        ]
        self._run(CopyStatic, ast)
        self.assertEqual(copyfile.call_count, 2)
