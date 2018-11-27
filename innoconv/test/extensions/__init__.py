"""Unit tests for extensions."""

# pylint: disable=missing-docstring

import unittest
from os.path import join

from innoconv.manifest import Manifest
from innoconv.test.utils import get_filler_content

SOURCE = '/source'
TARGET = '/target'
PATHS = (
    (),
    ('title-1',),
    ('title-2',),
    ('title-2', 'title-2-1'),
)


class TestExtension(unittest.TestCase):
    @staticmethod
    def _run(extension, ast=None, languages=('en', 'de')):
        if ast is None:
            ast = get_filler_content()
        title = {}
        for language in languages:
            title[language] = "Title ({})".format(language)
        manifest = Manifest({
            'languages': languages,
            'title': title,
        })
        ext = extension(manifest)
        ext.start(TARGET, SOURCE)
        for language in languages:
            ext.pre_conversion(language)
            ext.pre_process_file(language)
            ext.post_process_file(ast, "Welcome {}".format(language))
            ext.pre_process_file(join(language, 'title-1'))
            ext.post_process_file(ast, "Title 1 {}".format(language))
            ext.pre_process_file(join(language, 'title-2'))
            ext.post_process_file(ast, "Title 2 {}".format(language))
            ext.pre_process_file(join(language, 'title-2', 'title-2-1'))
            ext.post_process_file(ast, "Title 2-1 {}".format(language))
            ext.post_conversion(language)
        ext.finish()
        return ext
