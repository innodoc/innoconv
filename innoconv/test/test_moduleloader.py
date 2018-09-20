"""Unit tests for innoconv.modules.maketoc"""

# pylint: disable=missing-docstring

import unittest

# supress linting until tests are implemented
# pylint: disable=W0611

import innoconv.modloader as ml

MODLIST = ['demo',
           'maketoc']


class TestMod(ml.AbstractModule):
    """a Test Module"""

    def __init__(self):
        super(TestMod, self).__init__()
        self.events.extend([
            'test_not_implemented_event',
            'test_true_event'
        ])
        self.value = True

    def test_true_event(self):
        return self.value


class TestModLoad(unittest.TestCase):

    def __init__(self, arg):
        super(TestModLoad, self).__init__(arg)

    def test_run_mods(self):
        mod = TestMod()
        with self.assertRaises(NotImplementedError):
            ml.run_mods([mod], 'test_not_implemented_event')
        self.assertTrue(ml.run_mods([mod], 'test_true_event'))

    def test_mod_list(self):
        self.assertNotIn('blubb', ml.mod_list())
        for mod_name in MODLIST:
            self.assertIn(mod_name, ml.mod_list())

    def test_load_module(self):
        with self.assertRaises(RuntimeError):
            ml.load_module('blubb')
        demo = ml.load_module('demo')
        self.assertTrue(issubclass(type(demo), ml.AbstractModule))
