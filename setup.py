#!/usr/bin/env python3
# pylint: disable=missing-docstring,no-name-in-module,import-error

"""Define project commands."""


import distutils.cmd
from distutils.command.clean import clean
import os
import logging
import re
import subprocess
import sys
from setuptools import setup


ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
CONTENT_DIR = os.path.join(ROOT_DIR, 'content')
BUILD_DIR = os.path.join(ROOT_DIR, 'build')
PANZER_SUPPORT_DIR = os.path.join(ROOT_DIR, '.panzer')
LINT_DIRS = [
    os.path.join(ROOT_DIR, 'innoconv'),
    os.path.join(ROOT_DIR, 'setup.py'),
    os.path.join(PANZER_SUPPORT_DIR, 'filter')
]

TUB_BASE_REPO = 'git@gitlab.tubit.tu-berlin.de:innodoc/tub_base.git'
TUB_BASE_BRANCH = 'pandoc'

MINTMOD_BASE_URL = 'https://gitlab.tu-berlin.de/stefan.born/' \
                   'VEUNDMINT_TUB_Brueckenkurs/raw/multilang/src/tex/%s'


logging.basicConfig(level=logging.INFO, format='%(message)s')

METADATA_PATH = os.path.join(ROOT_DIR, 'innoconv', 'metadata.py')
with open(METADATA_PATH, 'r') as metadata_file:
    METADATA = dict(
        re.findall(r"__([a-z_]+)__\s*=\s*['\"]([^'\"]+)['\"]",
                   metadata_file.read()))


def get_logger():
    return logging.getLogger('setup.py')


class BaseCommand(distutils.cmd.Command):  # pylint: disable=no-member
    user_options = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log = get_logger()

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def _run(self, command, err_msg='Command failed!', cwd=ROOT_DIR):
        self.log.info('Command %s', ' '.join(command))

        # make mintmod_filter module available
        env = os.environ.copy()
        env['PYTHONPATH'] = ROOT_DIR

        proc = subprocess.Popen(
            command, cwd=cwd, env=env, stderr=subprocess.STDOUT)

        return_code = proc.wait(timeout=120)
        if return_code != 0:
            raise RuntimeError(err_msg)


class Flake8Command(BaseCommand):
    description = 'Run flake8 on Python source files'

    def run(self):
        self._run(['flake8'] + LINT_DIRS)


class PylintCommand(BaseCommand):
    description = 'Run pylint on Python source files'

    def run(self):
        self._run(['pylint', '--output-format=colorized'] + LINT_DIRS)


class TestCommand(BaseCommand):
    description = 'Run test suite'

    user_options = [
        ('test-target=', 't', 'Test target (module or path)'),
    ]

    def initialize_options(self):
        self.test_target = os.path.join(ROOT_DIR, 'innoconv')

    def run(self):
        self._run(['green', '-r', self.test_target])


class CoverageCommand(BaseCommand):
    description = 'Generate HTML coverage report'

    def run(self):
        if not os.path.isfile(os.path.join(ROOT_DIR, '.coverage')):
            self.log.error(
                'Run "./setup.py test" first to generate a ".coverage".')
        self._run(['coverage', 'html'])


class CleanCommand(clean, BaseCommand):
    def run(self):
        super().run()
        self._run(['rm', '-rf', BUILD_DIR])
        self._run(['rm', '-rf', CONTENT_DIR])
        self._run(['rm', '-rf', os.path.join(ROOT_DIR, 'htmlcov')])
        self._run(['rm', '-rf', os.path.join(ROOT_DIR, '.coverage')])


def setup_package():
    setup(
        name='innoconv',
        version=METADATA['version'],
        author=METADATA['author'],
        author_email=METADATA['author_email'],
        cmdclass={
            'clean': CleanCommand,
            'coverage': CoverageCommand,
            'flake8': Flake8Command,
            'pylint': PylintCommand,
            'test': TestCommand,
        },
        entry_points={
            'console_scripts': [
                'innoconv = innoconv.__main__:main',
                'mintmod_ifttm = innoconv.mintmod_ifttm:main',
            ],
        },
        include_package_data=True,
        packages=[
            'innoconv',
        ],
        keywords=['pandoc'],
        license=METADATA['license'],
        long_description=open('README.md').read(),
        url=METADATA['url'],
        zip_safe=False,
    )


if __name__ == '__main__':
    try:
        setup_package()
    except RuntimeError as err:
        get_logger().error('%s: %s', type(err).__name__, err)
        sys.exit(-1)
