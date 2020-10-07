"""Unit tests for extensions."""

from copy import deepcopy
from os.path import join
import unittest

from innoconv.ext.abstract import AbstractExtension
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
    """
    Provide a base class for all extension tests.

    This basically simulates a run without using
    :class:`InnoconvRunner <innoconv.runner.InnoconvRunner>`.
    """

    @staticmethod
    def _run(extension, ast=None, languages=("en", "de"), paths=PATHS, manifest=None):
        if ast is None:
            ast = get_filler_content()
        title = {}
        for language in languages:
            title[language] = f"Title ({language})"
        if manifest is None:
            manifest = Manifest(
                {"languages": languages, "title": title, "min_score": 90}
            )
        try:
            if issubclass(extension, AbstractExtension):
                ext = extension(manifest)
            else:
                raise ValueError("extension not a sub-class of AbstractExtension!")
        except TypeError:
            ext = extension
        ext.start(DEST, SOURCE)
        asts = []
        for language in languages:
            ext.pre_conversion(language)
            for title, path in paths:
                ext.pre_process_file(join(language, *path))
                file_ast = deepcopy(ast)
                asts.append(file_ast)
                file_title = f"{title} {language}"
                ext.post_process_file(file_ast, file_title, "section", "test")
            ext.post_conversion(language)
        ext.finish()
        return ext, asts
