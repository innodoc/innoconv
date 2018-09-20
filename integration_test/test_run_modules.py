"""Unit tests for innoconv.runner"""

# pylint: disable=missing-docstring

import unittest

# supress linting until tests are implemented
# pylint: disable=W0611,invalid-name
from innoconv.runner import InnoconvRunner  # noqa: F401
import innoconv.modloader as ml
from integration_test.fixtures.handler import FixturesHandler

fixtures = FixturesHandler()


class TestRunModules(unittest.TestCase):

    def __init__(self, arg):
        super(TestRunModules, self).__init__(arg)
        self.runner = None

    def test_run_modules(self):
        for mod_name in ml.mod_list():
            fixtures.prepare_fixtures()
            mod = ml.load_module(mod_name)
            self.runner = InnoconvRunner(source_dir=fixtures.SOURCE,
                                         output_dir_base=fixtures.TARGET,
                                         languages=['de'],
                                         modules=[mod])
            self.assertFalse(self.runner.run())
            fixtures.cleanup_fixtures()
