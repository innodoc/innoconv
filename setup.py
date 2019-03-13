#!/usr/bin/env python3
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

# Need to parse metadata manually as setup.py must not import innoconv
METADATA_PATH = os.path.join(ROOT_DIR, 'innoconv', 'metadata.py')
with open(METADATA_PATH, 'r') as metadata_file:
    METADATA = dict(
        re.findall(r"__([a-z_]+)__\s*=\s*['\"]([^'\"]+)['\"]",
                   metadata_file.read()))


with open('README.md', 'r') as fh:
    LONG_DESCRIPTION = fh.read()


def get_logger():
    """Get logger instance for setup.py."""
    return logging.getLogger('setup.py')


class BaseCommand(distutils.cmd.Command):  # pylint: disable=no-member
    """The base class for all custom commands."""

    user_options = []

    def __init__(self, *args, **kwargs):
        """Get logger."""
        super().__init__(*args, **kwargs)
        self.log = get_logger()

    def initialize_options(self):
        """Set default values for options."""

    def finalize_options(self):
        """Post-process options."""

    def _run(self, command, err_msg='Command failed!', cwd=ROOT_DIR):
        self.log.info('Command %s', ' '.join(command))
        proc = subprocess.Popen(command, cwd=cwd, stderr=subprocess.STDOUT)
        return_code = proc.wait(timeout=240)
        if return_code != 0:
            raise RuntimeError(err_msg)

    def _run_cmd(self, cmd):
        self._run([sys.executable, 'setup.py'] + cmd)


class Flake8Command(BaseCommand):
    """Custom command that runs flake8 on source files."""

    description = 'Run flake8 on Python source files.'

    def run(self):
        """Run command."""
        self._run(['flake8', '--max-complexity=10'] + LINT_DIRS)


class PylintCommand(BaseCommand):
    """Custom command that runs pylint on source files."""

    description = 'Run pylint on Python source files'

    def run(self):
        """Run command."""
        self._run(['pylint', '--output-format=colorized'] + LINT_DIRS)


class PyDocStyleCommand(BaseCommand):
    """Custom command that runs pydocstyle on source files."""

    description = 'Run pydocstyle on Python source files'

    def run(self):
        """Run command."""
#        self._run(['pydocstyle', '--ignore=D401'] + LINT_DIRS)
        self._run(['pydocstyle'] + LINT_DIRS)


class LintCommand(BaseCommand):
    """Custom command that runs all lint tools on source files."""

    description = 'Run all lint tools on Python source files'

    def run(self):
        """Run command."""
        self._run_cmd(['flake8'])
        self._run_cmd(['pylint'])
        self._run_cmd(['pydocstyle'])


class TestCommand(BaseCommand):
    """Custom command that runs unit tests on source files."""

    description = 'Run unit test suite'

    user_options = [
        ('test-target=', 't', 'Test target (module or path)'),
    ]

    def initialize_options(self):
        """Set default values for option for test_target."""
        self.test_target = os.path.join(ROOT_DIR, 'test')

    def run(self):
        """Run command."""
        self._run(['green', '-vv', '-r', self.test_target])


class CoverageCommand(BaseCommand):
    """Custom command that generates a HTML coverage report."""

    description = 'Generate HTML coverage report'

    def run(self):
        """Run command."""
        if not os.path.isfile(os.path.join(ROOT_DIR, '.coverage')):
            self.log.error('No ".coverage" found. Running tests first…')
            self._run_cmd(['test'])
        self._run(['coverage', 'html'])


class IntegrationTestCommand(BaseCommand):
    """Custom command that runs integration tests on source files."""

    description = 'Run integration test suite'

    user_options = [
        ('test-target=', 't', 'Test target (module or path)'),
    ]

    def initialize_options(self):
        """Set default values for option for test_target."""
        self.test_target = os.path.join(ROOT_DIR, 'integration_test')

    def run(self):
        """Run command."""
        self._run(['green', '-vv', self.test_target])


class CleanCommand(clean, BaseCommand):
    """Custom command that cleans all build files."""

    def run(self):
        """Run command."""
        super().run()
        self._run(['rm', '-rf', os.path.join(ROOT_DIR, 'htmlcov')])
        self._run(['rm', '-rf', os.path.join(ROOT_DIR, '.coverage')])
        self._run(['rm', '-rf', os.path.join(ROOT_DIR, 'innoconv.egg-info')])
        self._run(['rm', '-rf', os.path.join(ROOT_DIR, 'build')])
        self._run(['rm', '-rf', os.path.join(ROOT_DIR, 'dist')])


class UploadCommand(BaseCommand):
    """Custom command that uploads release to PyPI and tags it in git."""

    def run(self):
        """Run command."""
        self.log.info('Building distribution files (universal)…')
        self._run_cmd(['clean'])
        self._run_cmd(['sdist', 'bdist_wheel'])
        self.log.info('Uploading the package to PyPI via Twine…')
        self._run(['twine', 'upload', 'dist/*'])
        self.log.info('Pushing git tag…')
        self._run(['git', 'tag', f"v{METADATA['version']}"])
        self._run(['git', 'push', '--tags'])


def setup_package():
    """Create package setup information."""
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
        install_requires=['PyYAML>=3.13,<4'],
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
