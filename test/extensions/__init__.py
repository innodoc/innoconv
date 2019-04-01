"""Unit tests for extensions."""

from copy import deepcopy
from os.path import join
import unittest

from innoconv.manifest import Manifest
from ..utils import get_filler_content

SOURCE = "/source"
DEST = "/destination"
PATHS = (
    ("Welcome", ()),
    ("Title 1", ("title-1",)),
    ("Title 2", ("title-2",)),
    ("Title 2-1", ("title-2", "title-2-1")),
)
TEMP = "/temp"


class TestExtension(unittest.TestCase):
    """Provide a base class for all extension tests."""

    @staticmethod
    def _run(extension, ast=None, languages=("en", "de"), paths=PATHS):
        if ast is None:
            ast = get_filler_content()
        title = {}
        for language in languages:
            title[language] = "Title ({})".format(language)
        manifest = Manifest({"languages": languages, "title": title})
        ext = extension(manifest)
        ext.start(DEST, SOURCE)
        asts = []
        for language in languages:
            ext.pre_conversion(language)
            for title, path in paths:
                ext.pre_process_file(join(language, *path))
                file_ast = deepcopy(ast)
                asts.append(file_ast)
                file_title = "{} {}".format(title, language)
                ext.post_process_file(file_ast, file_title)
            ext.post_conversion(language)
        ext.finish()
        return ext, asts
