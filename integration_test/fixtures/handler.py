"""Handles fixtures"""

import os
import shutil
import time
import random
import string

# pylint: disable=W0611,invalid-name


class FixturesHandler:
    """Handles fixtures"""

    BASE_DIR = os.path.dirname(os.path.realpath(__file__))
    ORIGINAL = BASE_DIR + os.sep + "original"
    ORIGINAL_SOURCE = ORIGINAL + os.sep + "convertme"
    ORIGINAL_TARGET = ORIGINAL + os.sep + "target"
    ORIGINAL_EXPECTED = ORIGINAL + os.sep + "expected"
    BASE = BASE_DIR + os.sep + "working"
    SOURCE = BASE + os.sep + "convertme"
    SOURCE_STATIC = SOURCE + os.sep + "static"
    SOURCE_DE = SOURCE + os.sep + "de"
    SOURCE_FOLDER = SOURCE_DE + os.sep + "01 Test"
    SOURCE_FILE = SOURCE_FOLDER + os.sep + "content.md"
    TARGET = BASE + os.sep + "target"

    def __init__(self):
        self.BASE = self.BASE_DIR + os.sep +\
                    "working" + os.sep + \
                    ''.join(
                        random.choice(string.ascii_uppercase)
                        for _ in range(4))
        if not os.path.isdir(self.BASE_DIR + os.sep + "working"):
            os.mkdir(self.BASE_DIR + os.sep + "working")

        if not os.path.isdir(self.ORIGINAL_TARGET):
            os.mkdir(self.ORIGINAL_TARGET)

        os.mkdir(self.BASE)
        self.SOURCE = self.BASE + os.sep + "convertme"
        self.SOURCE_STATIC = self.SOURCE + os.sep + "static"
        self.SOURCE_DE = self.SOURCE + os.sep + "de"
        self.SOURCE_FOLDER = self.SOURCE_DE + os.sep + "01 Test"
        self.SOURCE_FILE = self.SOURCE_FOLDER + os.sep + "content.md"
        self.TARGET = self.BASE + os.sep + "target"

    def __del__(self):
        self.cleanup_fixtures()

    def prepare_fixtures(self):
        """Prepares the fixtures for testing"""
        success = False
        while not success:
            try:
                shutil.copytree(self.ORIGINAL_SOURCE, self.SOURCE)
                shutil.copytree(self.ORIGINAL_TARGET, self.TARGET)
                success = True
            except (FileExistsError, shutil.Error):
                self.cleanup_fixtures()
                time.sleep(1)

    def cleanup_fixtures(self):
        """Cleanes up the fixtures"""

        success = False
        while not success:
            try:
                if os.path.isdir(self.BASE):
                    shutil.rmtree(self.BASE)
                success = True
            except (FileNotFoundError, OSError):
                time.sleep(1)

    def delete_static(self):
        """Removes the static folder"""
        if os.path.isdir(self.SOURCE_STATIC):
            shutil.rmtree(self.SOURCE_STATIC)
