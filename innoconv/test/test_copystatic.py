"""Unit tests for Copying static files"""

# pylint: disable=missing-docstring

import os
import unittest
import mock

from innoconv.modules import Copystatic
from innoconv.constants import STATIC_FOLDER

# supress linting until tests are implemented
# pylint: disable=W0611,invalid-name

SOURCE = 'SOURCEPATH'
TARGET = 'TARGETPATH'


def get_filler_content():
    return {
        't': 'Str',
        'c': 'Lorem Ipsum'
    }


def get_filler_content2():
    return {
        't': 'placeholder',
        'c': [[], 1, []]
    }


def get_para_ast(content=None):
    if content is None:
        content = [
            get_filler_content()
        ]
    return {
        't': 'Para',
        'c': content
    }


def get_image_ast(path, title='', description=''):
    return {
        't': 'Image',
        'c': [
            [
                '',
                [],
                []
            ],
            [
                {
                    't': 'Str',
                    'c': title
                }
            ],
            [
                path,
                description
            ]
        ]
    }


def get_video_ast(path, title=''):
    return get_generic_link_ast([
        {
            't': 'Str',
            'c': title
        }
    ], path, title, [
        'video',
        'video-static'
    ])


def get_youtube_ast(url, title=''):
    return get_generic_link_ast([
        {
            't': 'Str',
            'c': title
        }
    ], url, title, [
        'video',
        'video-youtube'
    ])


def get_generic_link_ast(content, link, title='', classes=None):
    if classes is None:
        classes = []
    return {
        't': 'Link',
        'c': [
            [
                '',
                classes,
                []
            ],
            content,
            [
                link,
                title
            ]
        ]
    }


SOURCE_STRUCTURE = [
    os.path.join(SOURCE, STATIC_FOLDER, 'present.png'),
    os.path.join(SOURCE, STATIC_FOLDER, 'subfolder', 'present.png'),
    os.path.join(SOURCE, STATIC_FOLDER, 'subfolder', 'present.mp4'),
    os.path.join(SOURCE, STATIC_FOLDER, 'path', 'to', 'example_image.jpg'),
    os.path.join(SOURCE, STATIC_FOLDER, 'localizable.gif'),

    os.path.join(SOURCE, 'la', STATIC_FOLDER, 'localized_present.png'),
    os.path.join(SOURCE, 'la', STATIC_FOLDER, 'single_language.svg'),
    os.path.join(SOURCE, 'la', STATIC_FOLDER, 'subfolder',
                 'localized_present.mp4'),
    os.path.join(SOURCE, 'la', STATIC_FOLDER, 'localizable.gif'),
    os.path.join(SOURCE, 'la', STATIC_FOLDER, 'path', 'to',
                 'example_video.ogv'),

    os.path.join(SOURCE, 'en', STATIC_FOLDER, 'localized_present.png'),
    os.path.join(SOURCE, 'en', STATIC_FOLDER, 'subfolder',
                 'localized_present.mp4'),
    os.path.join(SOURCE, 'en', STATIC_FOLDER, 'path', 'to',
                 'example_video.ogv'),
]

AST_ABSOLUTE_PICTURE = [
    get_image_ast('/present.png')
]

AST_COMPLETE_PICTURE = [
    get_image_ast('/present.png', 'title', 'description')
]

AST_NO_PICTURE = [
    get_image_ast('/not-present.png')
]

AST_SUBFOLDER_PICTURE = [
    get_image_ast('/subfolder/present.png')
]

AST_RELATIVE_PICTURE = [
    get_image_ast('example_image.jpg')
]

AST_LOCALIZED_PICTURE = [
    get_image_ast('/localized_present.png')
]

AST_LOCALIZABLE_PICTURE = [
    get_image_ast('/localizable.gif')
]

AST_SINGLE_LANGUAGE_PICTURE = [
    get_image_ast('/single_language.svg')
]

AST_REMOTE_PICTURE = [
    get_image_ast('http://www.example.com/example.png')
]

AST_ABSOLUTE_VIDEO = [
    get_video_ast('/subfolder/present.mp4')
]

AST_RELATIVE_VIDEO = [
    get_video_ast('example_video.ogv')
]

AST_REMOTE_VIDEO = [
    get_video_ast('http://www.example.com/example.ogv')
]

AST_NO_VIDEO = [
    get_video_ast('/not-present.mp4')
]

AST_STACKED_SINGLE_PICTURE = [
    get_para_ast(),
    get_para_ast([get_image_ast('/present.png')]),
    get_para_ast([[get_para_ast()]]),
    get_para_ast([get_para_ast([get_para_ast()]), get_para_ast()])
]

AST_LINKED_PICTURE = [
    get_generic_link_ast(
        [get_image_ast('/present.png')],
        'http://www.tu-berlin.de')
]

AST_EXAMPLE = [
    get_para_ast(),
    get_para_ast([get_image_ast('/present.png', 'Image Present')]),
    get_para_ast([get_para_ast([get_image_ast('/subfolder/present.mp4')])]),
    get_para_ast([
        get_para_ast(get_para_ast()),
        get_para_ast([get_filler_content2()]),
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


def is_file_replace(path):
    for file_path in SOURCE_STRUCTURE:
        if file_path == path:
            return True
    return False


class CopyMocker:

    def __init__(self):
        super(CopyMocker, self).__init__()
        self.is_Localized = False
        self.copied_images = 0
        self.target = dict()
        self.language_starts = [
            os.path.join(SOURCE, 'la', STATIC_FOLDER),
            os.path.join(SOURCE, 'en', STATIC_FOLDER)
        ]

    def reset(self, full=False):
        self.is_Localized = False
        self.copied_images = 0
        if full:
            self.target = dict()

    def exists(self, path):
        folders = os.path.normpath(path).split(os.sep)
        curr = self.target
        for folder in folders:
            if folder in curr:
                curr = curr[folder]
            else:
                return False
        return True

    def make_directory(self, path, make_tree=True):
        head, tail = os.path.split(os.path.normpath(path))
        folders = head.split(os.sep)
        curr = self.target
        for folder in folders:
            if folder in curr:
                curr = curr[folder]
            elif make_tree:
                curr[folder] = {
                    '.': []
                }
                curr = curr[folder]
            else:
                raise OSError('make_directory, base dir not existing')
        curr[tail] = {
            '.': []
        }

    def remove_tree(self, path):
        self.make_directory(path, False)

    def copy_file(self, src, target):
        src_path, src_file = os.path.split(target)
        folders = src_path.split(os.sep)
        curr = self.target
        for folder in folders:
            if folder in curr:
                curr = curr[folder]
            else:
                raise OSError('copy_file, base dir not existing')
        curr['.'].append(src_file)
        self.copied_images += 1
        for lang_path in self.language_starts:
            if src.startswith(lang_path):
                self.is_Localized = True

    def copied_files(self, element=None):
        count = []
        if element is None:
            element = self.target
        for subelement in element:
            if subelement == '.':
                count += element[subelement]
            else:
                count += self.copied_files(element[subelement])
        return count


class TestCopyStatic(unittest.TestCase):

    def __init__(self, arg):
        super(TestCopyStatic, self).__init__(arg)
        self.cps = Copystatic()

    def setUp(self):
        self.cps = Copystatic()

        self.copy_mocker = CopyMocker()

    # pylint: disable=R0913
    def _perform_test(self, ast, is_localized=None,
                      expect_error=False, no_media=False, copied_images=1,
                      language='la', skip_creation=False, skip_resolve=False):

        if not skip_creation:
            self.cps.pre_conversion({
                "source": SOURCE,
                "output": TARGET
            })
            self.cps.pre_language(language)
            self.copy_mocker.reset(full=True)
        else:
            self.copy_mocker.reset(full=False)

        path = os.path.join(language, 'path', 'to')
        self.cps.pre_content_file(path, os.path.join(SOURCE, path))
        with mock.patch('os.path.isfile',
                        create=True) as mock_isFile:
            mock_isFile.side_effect = is_file_replace
            with mock.patch('shutil.copyfile',
                            create=True,
                            side_effect=self.copy_mocker.copy_file):
                with mock.patch('os.makedirs',
                                create=True,
                                side_effect=self.copy_mocker.make_directory):
                    with mock.patch('shutil.rmtree',
                                    create=True,
                                    side_effect=self.copy_mocker.remove_tree):
                        with mock.patch('os.path.lexists',
                                        create=True,
                                        side_effect=self.copy_mocker.exists):
                            if expect_error:
                                with self.assertRaises(RuntimeError):
                                    self.cps.process_ast(ast)
                                return
                            self.cps.process_ast(ast)
                            if not skip_resolve:
                                self.cps.post_conversion()
                                self.assertEqual(
                                    copied_images,
                                    self.copy_mocker.copied_images)
                                self.assertEqual(
                                    copied_images,
                                    len(self.copy_mocker.copied_files()))
                                if is_localized is not None:
                                    self.assertEqual(
                                        is_localized,
                                        self.copy_mocker.is_Localized)
                            if not no_media:
                                self.assertTrue(mock_isFile.called)

    def test_absolute_nonlocalized(self):
        self._perform_test(
            ast=AST_ABSOLUTE_PICTURE)

        self._perform_test(
            ast=AST_COMPLETE_PICTURE)

        self._perform_test(
            ast=AST_SUBFOLDER_PICTURE)

        self._perform_test(
            ast=AST_ABSOLUTE_VIDEO)

    def test_relative_nonlocalized(self):
        self._perform_test(
            ast=AST_RELATIVE_PICTURE)

    def test_remote(self):
        self._perform_test(
            ast=AST_REMOTE_PICTURE,
            copied_images=0,
            no_media=True)

        self._perform_test(
            ast=AST_REMOTE_VIDEO,
            copied_images=0,
            no_media=True)

    def test_absolute_localized(self):
        self._perform_test(
            ast=AST_LOCALIZED_PICTURE,
            is_localized=True)

        self._perform_test(
            ast=AST_LOCALIZED_PICTURE,
            is_localized=True,
            language='en')

        self._perform_test(
            ast=AST_LOCALIZABLE_PICTURE,
            is_localized=True)

        self._perform_test(
            ast=AST_LOCALIZABLE_PICTURE,
            is_localized=False,
            language='en')

        self._perform_test(
            ast=AST_SINGLE_LANGUAGE_PICTURE,
            is_localized=True)

    def test_relative_localized(self):
        self._perform_test(
            ast=AST_RELATIVE_VIDEO)

    def test_localizable(self):
        self._perform_test(
            ast=AST_LOCALIZABLE_PICTURE,
            is_localized=True)

        self._perform_test(
            ast=AST_LOCALIZABLE_PICTURE,
            is_localized=False,
            language='en')

    def test_errors(self):
        self._perform_test(
            ast=AST_NO_PICTURE,
            expect_error=True)

        self._perform_test(
            ast=AST_NO_VIDEO,
            expect_error=True)

        self._perform_test(
            ast=AST_SINGLE_LANGUAGE_PICTURE,
            is_localized=True,
            expect_error=True,
            language='en')

    def test_complex1(self):
        self._perform_test(
            ast=AST_STACKED_SINGLE_PICTURE)

        self._perform_test(
            ast=AST_LINKED_PICTURE)

    def test_complex2(self):
        self._perform_test(
            ast=AST_EXAMPLE,
            is_localized=True,
            copied_images=5)

        self._perform_test(
            ast=AST_EXAMPLE,
            is_localized=True,
            language='en',
            copied_images=5)

    def test_repeat_copy(self):
        self._perform_test(
            ast=AST_ABSOLUTE_PICTURE,
            skip_resolve=True)
        self._perform_test(
            ast=AST_ABSOLUTE_PICTURE,
            skip_creation=True,
            skip_resolve=True)
        self._perform_test(
            ast=AST_ABSOLUTE_PICTURE,
            skip_creation=True)

        self.cps.pre_conversion({
            "source": SOURCE,
            "output": TARGET
        })

        self._perform_test(
            ast=AST_SUBFOLDER_PICTURE,
            skip_creation=True,
            skip_resolve=True)
        self._perform_test(
            ast=AST_SUBFOLDER_PICTURE,
            skip_creation=True)

        self.cps.pre_conversion({
            "source": SOURCE,
            "output": TARGET
        })

        self._perform_test(
            ast=AST_ABSOLUTE_PICTURE,
            skip_creation=True,
            skip_resolve=True)
        self._perform_test(
            ast=AST_ABSOLUTE_PICTURE,
            skip_creation=True)
