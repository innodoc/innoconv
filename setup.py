#!/usr/bin/env python3
# pylint: disable=missing-docstring

"""Define project commands."""


import distutils.cmd
from distutils.command.clean import clean
import os
import logging
import re
import subprocess
import sys
from setuptools import setup, find_packages

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
LINT_DIRS = [
    os.path.join(ROOT_DIR, 'innoconv'),
    os.path.join(ROOT_DIR, 'setup.py'),
]

logging.basicConfig(level=logging.INFO, format='%(message)s')

METADATA_PATH = os.path.join(ROOT_DIR, 'innoconv', 'metadata.py')
with open(METADATA_PATH, 'r') as metadata_file:
    METADATA = dict(
        re.findall(r"__([a-z_]+)__\s*=\s*['\"]([^'\"]+)['\"]",
                   metadata_file.read()))


with open('README.md', 'r') as fh:
    LONG_DESCRIPTION = fh.read()


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
        proc = subprocess.Popen(command, cwd=cwd, stderr=subprocess.STDOUT)
        return_code = proc.wait(timeout=240)
        if return_code != 0:
            raise RuntimeError(err_msg)

    def _run_cmd(self, cmd):
        self._run([sys.executable, 'setup.py'] + cmd)


class Flake8Command(BaseCommand):
    description = 'Run flake8 on Python source files'

    def run(self):
        self._run(['flake8', '--max-complexity=10'] + LINT_DIRS)


class PylintCommand(BaseCommand):
    description = 'Run pylint on Python source files'

    def run(self):
        self._run(['pylint', '--output-format=colorized'] + LINT_DIRS)


class PyDocStyleCommand(BaseCommand):
    description = 'Run pydocstyle on Python source files'

    def run(self):
        self._run(['pydocstyle'] + LINT_DIRS)


class LintCommand(BaseCommand):
    description = 'Run pylint on Python source files'

    def run(self):
        self._run_cmd(['flake8'])
        self._run_cmd(['pylint'])
        self._run_cmd(['pydocstyle'])


class TestCommand(BaseCommand):
    description = 'Run test suite'

    user_options = [
        ('test-target=', 't', 'Test target (module or path)'),
    ]

    def initialize_options(self):
        self.test_target = os.path.join(ROOT_DIR, 'test')

    def run(self):
        self._run(['green', '-vv', '-r', self.test_target])


class CoverageCommand(BaseCommand):
    description = 'Generate HTML coverage report'

    def run(self):
        if not os.path.isfile(os.path.join(ROOT_DIR, '.coverage')):
            self.log.error('No ".coverage" found. Running tests first…')
            self._run_cmd(['test'])
        self._run(['coverage', 'html'])


class IntegrationTestCommand(BaseCommand):
    description = 'Run integration test suite'

    user_options = [
        ('test-target=', 't', 'Test target (module or path)'),
    ]

    def initialize_options(self):
        self.test_target = os.path.join(ROOT_DIR, 'integration_test')

    def run(self):
        self._run(['green', '-vv', self.test_target])


class CleanCommand(clean, BaseCommand):
    def run(self):
        super().run()
        self._run(['rm', '-rf', os.path.join(ROOT_DIR, 'htmlcov')])
        self._run(['rm', '-rf', os.path.join(ROOT_DIR, '.coverage')])
        self._run(['rm', '-rf', os.path.join(ROOT_DIR, 'innoconv.egg-info')])
        self._run(['rm', '-rf', os.path.join(ROOT_DIR, 'build')])
        self._run(['rm', '-rf', os.path.join(ROOT_DIR, 'dist')])


class UploadCommand(BaseCommand):
    def run(self):
        self.log.info('Building distribution files (universal)…')
        self._run_cmd(['clean'])
        self._run_cmd(['sdist', 'bdist_wheel'])
        self.log.info('Uploading the package to PyPI via Twine…')
        self._run(['twine', 'upload', 'dist/*'])
        self.log.info('Pushing git tag…')
        self._run(['git', 'tag', f"v{METADATA['version']}"])
        self._run(['git', 'push', '--tags'])


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
            'integration_test': IntegrationTestCommand,
            'pydocstyle': PyDocStyleCommand,
            'lint': LintCommand,
            'pylint': PylintCommand,
            'test': TestCommand,
            'upload': UploadCommand,
        },
        description='Converter for interactive educational content.',
        entry_points={
            'console_scripts': [
                'innoconv = innoconv.__main__:main',
            ],
        },
        extras_require={
            'dev': [
                'coverage',
                'flake8',
                'green',
                'mccabe',
                'pydocstyle',
                'pylint',
            ],
            'doc': [
                'sphinx-argparse',
                'sphinx-rtd-theme',
                'Sphinx',
            ],
        },
        include_package_data=True,
        install_requires=['PyYAML>=3,<4'],
        packages=find_packages(exclude=[
            'test',
            'test.*',
            'integration_test',
            'integration_test.*',
        ]),
        python_requires='>=3.6.0',
        keywords=['innodoc', 'pandoc', 'markdown', 'education'],
        license=METADATA['license'],
        long_description=LONG_DESCRIPTION,
        long_description_content_type='text/markdown',
        url=METADATA['url'],
        zip_safe=False,
        project_urls={
            'Documentation': 'https://readthedocs.org/projects/innoconv/',
        },
        classifiers=(
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.6',
            'License :: OSI Approved :: ' +
            'GNU General Public License v3 or later (GPLv3+)',
            'Operating System :: POSIX :: Linux',
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Intended Audience :: Education',
            'Topic :: Education',
            'Topic :: Text Processing :: Markup',
        ),
    )


if __name__ == '__main__':
    try:
        setup_package()
    except RuntimeError as err:
        get_logger().error('%s: %s', type(err).__name__, err)
        sys.exit(-1)
