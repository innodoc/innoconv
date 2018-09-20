""" Copies the statci subfolder """

import os.path
import os
import shutil

from innoconv.utils import log
from innoconv.modloader import AbstractModule
from innoconv.constants import STATIC_FOLDER


class Cpystatic(AbstractModule):
    """a Demo Module"""

    def __init__(self):
        super(Cpystatic, self).__init__()
        self.root = ''
        self.target = ''
        self.events.extend([
            "pre_conversion",
            "post_conversion"
        ])

    def pre_conversion(self, base_dirs):
        """store the output directory"""
        self.set_root(base_dirs["source"])
        self.set_target(base_dirs["output"])

    def post_conversion(self, ):
        """Copy the static folder"""
        self.copy_static()

    def set_root(self, root):
        """Sets the root for the source folder to copy from"""
        self.root = root

    def set_target(self, target):
        """Sets the target to copy to"""
        self.target = target

    def _static_folder(self):
        return self.root + os.sep + STATIC_FOLDER

    def _target_folder(self):
        return self.target + os.sep + STATIC_FOLDER

    def has_static(self):
        """Checks if there is a static fodler to copy"""
        return os.path.isdir(self._static_folder())

    def has_target_static(self):
        """Checks if there is a static fodler to copy"""
        return os.path.isdir(self._target_folder())

    def copy_static(self):
        """actually copies the folder"""
        if self.has_target_static():
            shutil.rmtree(self._target_folder())
        if self.has_static():
            log('Copying {} to {}'.format(self._static_folder(), self.target))
            shutil.copytree(self._static_folder(), self._target_folder())
