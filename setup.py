#!/usr/bin/env python3
# pylint: disable=missing-docstring,no-name-in-module,import-error

"""Define project commands."""


import distutils.cmd
from distutils.command.clean import clean
import os
import logging
from subprocess import Popen, PIPE
import sys
from setuptools import setup
from colorama import init as colorama_init, Style


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
colorama_init()


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
        self.log.info(
            '%sCommand%s %s', Style.BRIGHT, Style.NORMAL, ' '.join(command))
        # make mintmod_filter module available
        env = os.environ.copy()
        env['PYTHONPATH'] = ROOT_DIR

        proc = Popen(command, cwd=cwd, env=env, stdout=PIPE, stderr=PIPE)
        out, err_out = proc.communicate()
        if out:
            self.log.info(out.decode('utf-8'))
        if err_out:
            self.log.error(err_out.decode('utf-8'))
        if proc.returncode != 0:
            raise RuntimeError(err_msg)


# TODO: this should be named BuildProjectCommand and work for arbitrary
#       local/remote projects
class BuildTUBBaseCommand(BaseCommand):
    description = 'Build tub_base content'

    def run(self):
        project_root = os.path.join(CONTENT_DIR, 'tub_base')
        # TODO: this should work for arbitrary language codes
        project_root_lang = os.path.join(project_root, 'de')

        # clone source
        self._run(['mkdir', '-p', CONTENT_DIR])
        if os.path.isdir(project_root):
            self.log.info('Content source directory already exists.')
        else:
            self.log.info('Cloning source repository.')
            self._run(
                ['git', 'clone', '-q', '-b', TUB_BASE_BRANCH, TUB_BASE_REPO],
                cwd=CONTENT_DIR)

        # fetch de.tex
        filename_base = 'de.tex'
        filename_path = os.path.join(project_root_lang, filename_base)
        if os.path.isfile(filename_path):
            self.log.info('File already exists: %s', filename_base)
        else:
            self.log.info('Fetching file: %s', filename_base)
            self._run(['wget', '--quiet', MINTMOD_BASE_URL % filename_base],
                      cwd=project_root_lang)

        # prepare panzer
        filename_out_path = os.path.join(BUILD_DIR, 'tub_base', 'de')
        filename_out = os.path.join(filename_out_path, 'index.html')
        self._run(['mkdir', '-p', filename_out_path])
        cmd = [
            'panzer',
            '---panzer-support', PANZER_SUPPORT_DIR,
            '--metadata=style:innoconv',
            '--from=latex+raw_tex',
            '--to=html5',
            '--standalone',
            '--normalize',
            '--output=%s' % filename_out,
            'tree_pandoc.tex'
        ]

        # run panzer
        self._run(cmd, cwd=project_root_lang)

        self.log.info(
            '%sBuild finished:%s %s', Style.BRIGHT, Style.NORMAL, filename_out)


class Flake8Command(BaseCommand):
    description = 'Run flake8 on Python source files'

    def run(self):
        self._run(['flake8'] + LINT_DIRS)


class PylintCommand(BaseCommand):
    description = 'Run pylint on Python source files'

    def run(self):
        self._run(
            ['pylint', '--output-format=colorized'] + LINT_DIRS)


class TestCommand(BaseCommand):
    description = 'Run test suite'

    def run(self):
        self._run(['green', '-r', 'innoconv'])


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
    metadata = dict(
        name='innoConv',
        version='0.1',
        author='innoCampus',
        author_email='dietrich@math.tu-berlin.de',
        cmdclass={
            'build_tub_base': BuildTUBBaseCommand,
            'clean': CleanCommand,
            'coverage': CoverageCommand,
            'flake8': Flake8Command,
            'pylint': PylintCommand,
            'test': TestCommand,
        },
        entry_points={
            'console_scripts': [
                'mintmod_filter = innoconv.mintmod_filter.__main__:main',
            ],
        },
        packages=[
            'innoconv',
        ],
        license='GPLv3',
        long_description=open('README.md').read(),
    )
    setup(**metadata)


if __name__ == '__main__':
    try:
        setup_package()
    except RuntimeError as err:
        get_logger().error('%s: %s', type(err).__name__, err)
        sys.exit(-1)
