#!/usr/bin/env python3
import distutils.cmd
from distutils.command.clean import clean
import os
from setuptools import setup
from setuptools.command.test import test as SetuptoolsTestCommand
import subprocess
import sys
from pip.commands.install import logger


ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
TUB_BASE_REPO = 'git@gitlab.tubit.tu-berlin.de:innodoc/tub_base.git'
TUB_BASE_BRANCH = 'pandoc'

MINTMOD_BASE_URL = 'https://gitlab.tu-berlin.de/stefan.born/' + \
                   'VEUNDMINT_TUB_Brueckenkurs/raw/multilang/src/tex/%s'


def _run(command, err_msg='Command failed!', cwd=ROOT_DIR):
    logger.info('Running command %s', command)
    # make mintmod_filter module available
    env = os.environ.copy()
    env['PYTHONPATH'] = ROOT_DIR

    proc = subprocess.Popen(command, cwd=cwd, env=env)
    out, err = proc.communicate()
    if out:
        logger.log(out)
    if err:
        logger.error(err)
    if proc.returncode != 0:
        raise RuntimeError(err_msg)


class BaseCommand(distutils.cmd.Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


class BuildTUBBaseCommand(BaseCommand):
    description = 'Build tub_base content'

    def run(self):
        # clone source
        _run(['mkdir', '-p', 'content'])
        if not os.path.isdir(os.path.join(ROOT_DIR, 'content', 'tub_base')):
            _run(['git', 'clone', '-q', '-b', TUB_BASE_BRANCH, TUB_BASE_REPO],
                 cwd=os.path.join(ROOT_DIR, 'content'))
        # fetch de.tex
        _run(['wget', '--quiet', MINTMOD_BASE_URL % 'de.tex'],
             cwd=os.path.join(ROOT_DIR, 'content', 'tub_base', 'de'))
        # build html
        _run(['pandoc', '--from=latex+raw_tex', '--to=html5+empty_paragraphs',
              '--standalone', '--mathjax',
              '--filter=../../../mintmod_filter/__main__.py',
              '--output=tree_pandoc.html', 'tree_pandoc.tex'],
             cwd=os.path.join(ROOT_DIR, 'content', 'tub_base', 'de'))


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
        _run(['rm', '-rf', os.path.join(ROOT_DIR, 'content')])
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
        logger.error('%s: %s' % (type(err).__name__, err))
        sys.exit(-1)
