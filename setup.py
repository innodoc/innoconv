#!/usr/bin/env python3
import distutils.cmd
from distutils.command.clean import clean
import os
import logging
from setuptools import setup
from setuptools.command.test import test as SetuptoolsTestCommand
import subprocess
import sys
from colorama import init as colorama_init, Style


ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
CONTENT_ROOT = os.path.join(ROOT_DIR, 'content')
TUB_BASE_REPO = 'git@gitlab.tubit.tu-berlin.de:innodoc/tub_base.git'
TUB_BASE_BRANCH = 'pandoc'

MINTMOD_BASE_URL = 'https://gitlab.tu-berlin.de/stefan.born/' + \
                   'VEUNDMINT_TUB_Brueckenkurs/raw/multilang/src/tex/%s'


logging.basicConfig(level=logging.INFO, format='%(message)s')
log = logging.getLogger('setup.py')
colorama_init()


def _run(command, err_msg='Command failed!', cwd=ROOT_DIR):
    log.info('%sCommand%s %s' % (
        Style.BRIGHT, Style.NORMAL, ' '.join(command)))
    # make mintmod_filter module available
    env = os.environ.copy()
    env['PYTHONPATH'] = ROOT_DIR

    proc = subprocess.Popen(command, cwd=cwd, env=env)
    out, err = proc.communicate()
    if out:
        log.info(out)
    if err:
        log.error(err)
    if proc.returncode != 0:
        raise RuntimeError(err_msg)


class BaseCommand(distutils.cmd.Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


# TODO: this should be named BuildProjectCommand and work for arbitrary
#       local/remote projects
class BuildTUBBaseCommand(BaseCommand):
    description = 'Build tub_base content'

    def run(self):
        project_root = os.path.join(CONTENT_ROOT, 'tub_base')
        # TODO: this should work for arbitrary language codes
        project_root_lang = os.path.join(project_root, 'de')

        # clone source
        _run(['mkdir', '-p', 'content'])
        if os.path.isdir(project_root):
            log.info('Content source directory already exists.')
        else:
            log.info('Cloning source repository.')
            _run(['git', 'clone', '-q', '-b', TUB_BASE_BRANCH, TUB_BASE_REPO],
                 cwd=CONTENT_ROOT)

        # fetch de.tex
        filename_base = 'de.tex'
        filename_path = os.path.join(project_root_lang, filename_base)
        if os.path.isfile(filename_path):
            log.info('File already exists: %s' % filename_base)
        else:
            log.info('Fetching file: %s' % filename_base)
            _run(['wget', '--quiet', MINTMOD_BASE_URL % filename_base],
                 cwd=project_root_lang)

        # build html
        _run(['pandoc', '--from=latex+raw_tex', '--to=html5+empty_paragraphs',
              '--standalone', '--mathjax',
              '--filter=../../../mintmod_filter/__main__.py',
              '--output=tree_pandoc.html', 'tree_pandoc.tex'],
             cwd=project_root_lang)


class LintCommand(BaseCommand):
    description = 'Run flake8 on Python source files'

    def run(self):
        _run(['flake8', 'mintmod_filter', 'setup.py'])


class TestCommand(SetuptoolsTestCommand):
    description = 'Run test suite'

    def run(self):
        _run(['green', '-r', 'mintmod_filter'])


class CoverageCommand(BaseCommand):
    description = 'Generate HTML coverage report'

    def run(self):
        _run(['coverage', 'html'])


class CleanCommand(clean):
    def run(self):
        super().run()
        _run(['rm', '-rf', os.path.join(ROOT_DIR, 'build', 'sphinx')])
        _run(['rm', '-rf', CONTENT_ROOT])
        _run(['rm', '-rf', os.path.join(ROOT_DIR, 'htmlcov')])
        _run(['rm', '-rf', os.path.join(ROOT_DIR, '.coverage')])


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
            'lint': LintCommand,
            'test': TestCommand,
        },
        entry_points={
            'console_scripts': [
                'mintmod_filter = mintmod_filter.__main__:main',
            ],
        },
        packages=[
            'mintmod_filter',
        ],
        license='GPLv3',
        long_description=open('README.md').read(),
    )
    setup(**metadata)


if __name__ == '__main__':
    try:
        setup_package()
    except RuntimeError as err:
        log.error('%s: %s' % (type(err).__name__, err))
        sys.exit(-1)
