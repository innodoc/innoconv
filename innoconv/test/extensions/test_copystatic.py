"""Unit tests for Copying static files"""

# pylint: disable=missing-docstring

import os
import unittest
import itertools
import mock

from innoconv.extensions.copystatic import CopyStatic
from innoconv.constants import STATIC_FOLDER
from innoconv.test.utils import (
    get_filler_content, get_image_ast, get_video_ast, get_generic_link_ast,
    get_para_ast, get_youtube_ast)

SOURCE = '/source'
TARGET = '/target'


@mock.patch('os.makedirs', return_value=True)
@mock.patch('os.path.lexists', return_value=True)
@mock.patch('os.path.isfile', return_value=True)
@mock.patch('shutil.copyfile')
class TestCopyStatic(unittest.TestCase):

    @staticmethod
    def _run(ast, languages=('en', )):
        cps = CopyStatic()
        cps.init(languages, TARGET, SOURCE)
        for language in languages:
            cps.pre_conversion(language)
            relpath = os.path.join(language, 'path', 'to')
            cps.pre_process_file(relpath)
            cps.post_process_file(ast)
            cps.post_conversion(language)
        cps.finish()

    def test_make_target_dirs(self, *args):
        _, _, lexists, makedirs = args
        lexists.return_value = False
        ast = [get_image_ast('test.png')]
        self._run(ast)
        self.assertEqual(makedirs.call_count, 1)
        self.assertEqual(makedirs.call_args, mock.call(
            os.path.join(TARGET, 'en', STATIC_FOLDER, 'path', 'to')
        ))

    def test_relative_two_langs(self, copyfile, *_):
        languages = ('de', 'en')
        ast = [get_image_ast('localized_present.png')]
        self._run(ast, languages=languages)
        self.assertEqual(copyfile.call_count, 2)
        for lang in languages:
            src = os.path.join(
                SOURCE, lang, STATIC_FOLDER, 'path', 'to',
                'localized_present.png')
            target = os.path.join(
                TARGET, lang, STATIC_FOLDER, 'path', 'to',
                'localized_present.png')
            call = mock.call(src, target)
            self.assertIn(call, copyfile.call_args_list)

    def test_relative_nonlocalized(self, copyfile, isfile, *_):
        isfile.side_effect = itertools.cycle((False, True))
        self._run([get_image_ast('example_image.jpg')])
        self.assertEqual(copyfile.call_count, 1)
        src = os.path.join(
            SOURCE, STATIC_FOLDER, 'path', 'to', 'example_image.jpg')
        target = os.path.join(
            TARGET, STATIC_FOLDER, 'path', 'to', 'example_image.jpg')
        self.assertEqual(mock.call(src, target), copyfile.call_args)

    def test_absolute_nonlocalized(self, copyfile, isfile, *_):
        isfile.side_effect = itertools.cycle((False, True))
        self._run([get_image_ast('/present.jpg')])
        self.assertEqual(copyfile.call_count, 1)
        src = os.path.join(SOURCE, STATIC_FOLDER, 'present.jpg')
        target = os.path.join(TARGET, STATIC_FOLDER, 'present.jpg')
        self.assertEqual(mock.call(src, target), copyfile.call_args)

    def test_relative_localized(self, copyfile, *_):
        self._run([get_video_ast('example_video.ogv')])
        self.assertEqual(copyfile.call_count, 1)
        src = os.path.join(
            SOURCE, 'en', STATIC_FOLDER, 'path', 'to', 'example_video.ogv')
        target = os.path.join(
            TARGET, 'en', STATIC_FOLDER, 'path', 'to', 'example_video.ogv')
        self.assertEqual(mock.call(src, target), copyfile.call_args)

    def test_absolute_localized(self, copyfile, *_):
        self._run([get_image_ast('/present.jpg')])
        self.assertEqual(copyfile.call_count, 1)
        src = os.path.join(SOURCE, 'en', STATIC_FOLDER, 'present.jpg')
        target = os.path.join(TARGET, 'en', STATIC_FOLDER, 'present.jpg')
        self.assertEqual(mock.call(src, target), copyfile.call_args)

    def test_ignore_remote(self, copyfile, *_):
        tests = (
            'http://www.example.com/example.png',
            'http://www.example.com/example.png',
            'ftp://ftp.example.com/example.png',
        )
        for addr in tests:
            with self.subTest(addr):
                self._run([get_image_ast(addr)])
                self.assertEqual(copyfile.call_count, 0)

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
        self._run(ast)
        self.assertEqual(copyfile.call_count, 5)

    def test_stacked_single_picture(self, copyfile, *_):
        ast = [
            get_para_ast(),
            get_para_ast([get_image_ast('/present.png')]),
            get_para_ast([[get_para_ast()]]),
            get_para_ast([get_para_ast([get_para_ast()]), get_para_ast()])
        ]
        self._run(ast)
        self.assertEqual(copyfile.call_count, 1)

    def test_linked_picture(self, copyfile, *_):
        ast = [get_generic_link_ast(
            [get_image_ast('/present.png')],
            'http://www.tu-berlin.de')]
        self._run(ast)
        self.assertEqual(copyfile.call_count, 1)

    def test_file_does_not_exist(self, *args):
        _, isfile, _, _ = args
        isfile.return_value = False
        tests = (
            ('/not-present.png', [get_image_ast('/not-present.png')]),
            ('/not-present.mp4', [get_video_ast('/not-present.mp4')]),
            ('/single_language.svg', [get_image_ast('/single_language.svg')]),
        )
        for name, ast in tests:
            with self.subTest(name):
                with self.assertRaises(RuntimeError):
                    self._run(ast)

    def test_only_en_present(self, copyfile, isfile, *_):
        isfile.side_effect = itertools.cycle((True, False))
        self._run([get_image_ast('localizable.gif')], languages=('en', 'la'))
        self.assertEqual(copyfile.call_count, 2)
        src = os.path.join(
            SOURCE, STATIC_FOLDER, 'path', 'to', 'localizable.gif')
        target = os.path.join(
            TARGET, STATIC_FOLDER, 'path', 'to', 'localizable.gif')
        call = mock.call(src, target)
        self.assertIn(call, copyfile.call_args_list)
        src = os.path.join(
            SOURCE, 'en', STATIC_FOLDER, 'path', 'to', 'localizable.gif')
        target = os.path.join(
            TARGET, 'en', STATIC_FOLDER, 'path', 'to', 'localizable.gif')
        call = mock.call(src, target)
        self.assertIn(call, copyfile.call_args_list)

    def test_ignore_youtube(self, copyfile, *_):
        ast = [get_youtube_ast(
            'https://www.youtube.com/watch?v=C0DPdy98e4c', title='Test video')]
        self._run(ast)
        self.assertEqual(copyfile.call_count, 0)
