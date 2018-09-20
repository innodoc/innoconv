"""Unit tests for Copying static files"""

# pylint: disable=missing-docstring

import unittest
import mock

from innoconv.modules.cpystatic.cpystatic import Cpystatic

# supress linting until tests are implemented
# pylint: disable=W0611,invalid-name

SOURCE = "SOURCE"
TARGET = "TARGET"


class TestMaketoc(unittest.TestCase):

    def _is_dir(self, dirname):
        if SOURCE in dirname:
            return self.has_Static
        if TARGET in dirname:
            return self.has_Target_Static
        return False

    def _copytree(self, sourcedir, targetdir):
        if SOURCE in sourcedir:
            if TARGET in targetdir:
                self.has_Target_Static = True

    def setUp(self):
        self.cps.set_root(SOURCE)
        self.cps.set_target(TARGET)
        self.has_Static = True
        self.has_Target_Static = False

        os_path_isdir_patcher = mock.patch('os.path.isdir')
        self.os_path_isdir_mock = os_path_isdir_patcher.start()
        self.os_path_isdir_mock.side_effect = self._is_dir

        os_path_isfile_patcher = mock.patch('os.path.isfile')
        self.os_path_isfile_mock = os_path_isfile_patcher.start()
        self.os_path_isfile_mock.return_value = True

        shutil_rmtree_patcher = mock.patch('shutil.rmtree')
        self.shutil_rmtree_mock = shutil_rmtree_patcher.start()

        shutil_copytree_patcher = mock.patch('shutil.copytree')
        self.shutil_copytree_mock = shutil_copytree_patcher.start()
        self.shutil_copytree_mock.side_effect = self._copytree

        self.addCleanup(mock.patch.stopall)

    def __init__(self, arg):
        super(TestMaketoc, self).__init__(arg)
        self.cps = Cpystatic()
        self.has_Static = True
        self.has_Target_Static = False

    def test_pre_conversion(self):
        self.cps.root = ''
        self.cps.target = ''
        self.cps.pre_conversion({"source": 'A', "output": 'B'})
        self.assertEqual(self.cps.root, 'A')
        self.assertEqual(self.cps.target, 'B')

    def test_post_conversion(self):
        self.assertFalse(self.cps.has_target_static())
        self.cps.post_conversion()
        self.assertTrue(self.cps.has_target_static())
        self.assertTrue(self.os_path_isdir_mock.called)
        self.assertTrue(self.shutil_copytree_mock)

    def test_has_static(self):
        self.assertTrue(self.cps.has_static())
        self.assertTrue(self.os_path_isdir_mock.called)
        self.os_path_isdir_mock.reset_mock()
        self.has_Static = False
        self.assertFalse(self.cps.has_static())
        self.assertTrue(self.os_path_isdir_mock.called)

    def test_copy_static(self):
        self.assertFalse(self.cps.has_target_static())
        self.cps.post_conversion()
        self.assertTrue(self.cps.has_target_static())
        self.assertTrue(self.os_path_isdir_mock.called)
        self.assertTrue(self.shutil_copytree_mock)

    def test_double_copy(self):
        self.assertFalse(self.cps.has_target_static())
        self.cps.copy_static()
        self.assertTrue(self.cps.has_target_static())
        self.assertTrue(self.os_path_isdir_mock.called)
        self.assertTrue(self.shutil_copytree_mock.called)
        self.assertFalse(self.shutil_rmtree_mock.called)
        self.os_path_isdir_mock.reset_mock()
        self.shutil_copytree_mock.reset_mock()
        self.shutil_rmtree_mock.reset_mock()

        self.assertTrue(self.cps.has_target_static())
        self.assertTrue(self.os_path_isdir_mock.called)
        self.os_path_isdir_mock.reset_mock()

        self.assertTrue(self.cps.has_target_static())
        self.cps.copy_static()
        self.assertTrue(self.os_path_isdir_mock.called)
        self.assertTrue(self.cps.has_target_static())
        self.assertTrue(self.shutil_copytree_mock.called)
        self.assertTrue(self.shutil_rmtree_mock.called)
        self.os_path_isdir_mock.reset_mock()
        self.shutil_copytree_mock.reset_mock()
        self.shutil_rmtree_mock.reset_mock()

    def test_copy_nostatic(self):
        self.has_Static = False
        self.assertFalse(self.cps.has_static())
        self.assertFalse(self.cps.has_target_static())
        self.os_path_isdir_mock.reset_mock()
        self.cps.copy_static()
        self.assertTrue(self.os_path_isdir_mock.called)
        self.assertFalse(self.cps.has_static())
        self.assertFalse(self.cps.has_target_static())
        self.assertFalse(self.shutil_copytree_mock.called)
        self.assertFalse(self.shutil_rmtree_mock.called)
