#!/usr/bin/env python3
# pylint: disable=missing-docstring

"""Define project commands."""


import distutils.cmd
from distutils.command.clean import clean
import os
import logging
import subprocess
import sys
from setuptools import setup
from colorama import init as colorama_init, Style


ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
CONTENT_ROOT = os.path.join(ROOT_DIR, 'content')
BUILD_ROOT = os.path.join(ROOT_DIR, 'build')

TUB_BASE_REPO = 'git@gitlab.tubit.tu-berlin.de:innodoc/tub_base.git'
TUB_BASE_BRANCH = 'pandoc'

MINTMOD_BASE_URL = 'https://gitlab.tu-berlin.de/stefan.born/' \
                   'VEUNDMINT_TUB_Brueckenkurs/raw/multilang/src/tex/%s'

BOOTSTRAP_CSS = 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/' \
                'bootstrap.min.css'

logging.basicConfig(level=logging.INFO, format='%(message)s')
colorama_init()


def get_logger():
    return logging.getLogger('setup.py')


class BaseCommand(distutils.cmd.Command):
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

        proc = subprocess.Popen(command, cwd=cwd, env=env)
        out, err_out = proc.communicate()
        if out:
            self.log.info(out)
        if err_out:
            self.log.error(err_out)
        if proc.returncode != 0:
            raise RuntimeError(err_msg)


# TODO: this should be named BuildProjectCommand and work for arbitrary
#       local/remote projects
class BuildTUBBaseCommand(BaseCommand):
    description = 'Build tub_base content'

    def run(self):
        project_root = os.path.join(CONTENT_ROOT, 'tub_base')
        # TODO: this should work for arbitrary language codes
        project_root_lang = os.path.join(project_root, 'de')

        # clone source
        self._run(['mkdir', '-p', CONTENT_ROOT])
        if os.path.isdir(project_root):
            self.log.info('Content source directory already exists.')
        else:
            self.log.info('Cloning source repository.')
            self._run(
                ['git', 'clone', '-q', '-b', TUB_BASE_BRANCH, TUB_BASE_REPO],
                cwd=CONTENT_ROOT)

        # fetch de.tex
        filename_base = 'de.tex'
        filename_path = os.path.join(project_root_lang, filename_base)
        if os.path.isfile(filename_path):
            self.log.info('File already exists: %s', filename_base)
        else:
            self.log.info('Fetching file: %s', filename_base)
            self._run(['wget', '--quiet', MINTMOD_BASE_URL % filename_base],
                      cwd=project_root_lang)

        # build html
        filename_out_path = os.path.join(BUILD_ROOT, 'tub_base', 'de')
        filename_out = os.path.join(filename_out_path, 'index.html')
        self._run(['mkdir', '-p', filename_out_path])
        self._run(['pandoc', '--from=latex+raw_tex', '--to=html5',
                   '--standalone', '--mathjax',
                   # enable ifttm_filter
                   # '--filter=../../../innoconv/ifttm_filter/__main__.py',
                   '--filter=../../../innoconv/mintmod_filter/__main__.py',
                   '--css=%s' % BOOTSTRAP_CSS,
                   '--output=%s' % filename_out, 'tree_pandoc.tex'],
                  cwd=project_root_lang)

        self.log.info(
            '%sBuild finished:%s %s', Style.BRIGHT, Style.NORMAL, filename_out)


class Flake8Command(BaseCommand):
    description = 'Run flake8 on Python source files'

    def run(self):
        self._run(['flake8', 'innoconv', 'setup.py'])


class PylintCommand(BaseCommand):
    description = 'Run pylint on Python source files'

    def run(self):
        self._run(['pylint', '--output-format=colorized', 'innoconv'])


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
        self._run(['rm', '-rf', BUILD_ROOT])
        self._run(['rm', '-rf', CONTENT_ROOT])
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
