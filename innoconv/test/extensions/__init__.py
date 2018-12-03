"""Unit tests for extensions."""

# pylint: disable=missing-docstring

import unittest
from os.path import join

from innoconv.manifest import Manifest
from innoconv.test.utils import get_filler_content


def make_title(string_title, language):
    str_array = string_title.split(' ')
    title_ast = []
    for title_part in str_array:
        title_ast.append({
            't': "Str",
            'c': title_part
        })
        title_ast.append({
            't': "Space"
        })
    title_ast.append({
        't': "Str",
        'c': language
    })
    return title_ast


SOURCE = '/source'
TARGET = '/target'
PATHS = (
    ("Welcome", ()),
    ("Title 1", ('title-1',)),
    ("Title 2", ('title-2',)),
    ("Title 2-1", ('title-2', 'title-2-1')),
)
TEMP = '/TEMP'


class TestExtension(unittest.TestCase):
    @staticmethod
    def _run(extension, ast=None, languages=('en', 'de'), paths=PATHS,
             file_title=None):
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
            for title, path in paths:
                ext.pre_process_file(join(language, *path))
                if file_title is not None:
                    title = file_title
                else:
                    title = make_title(title, language)
                ext.post_process_file(ast, title)
            ext.post_conversion(language)
        ext.finish()
        return ext
