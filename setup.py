#!/usr/bin/env python3
"""Define project commands."""

import os
import logging
import re
import sys
from setuptools import setup, find_packages

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

logging.basicConfig(level=logging.INFO, format='%(message)s')

# Need to parse metadata manually as setup.py must not import innoconv
METADATA_PATH = os.path.join(ROOT_DIR, 'innoconv', 'metadata.py')
with open(METADATA_PATH, 'r') as metadata_file:
    METADATA = dict(
        re.findall(r"__([a-z_]+)__\s*=\s*['\"]([^'\"]+)['\"]",
                   metadata_file.read()))


with open('README.md', 'r') as fh:
    LONG_DESCRIPTION = fh.read()


# class UploadCommand(BaseCommand):
#     """Custom command that uploads release to PyPI and tags it in git."""
#
#     def run(self):
#         """Run command."""
#         self.log.info('Building distribution files (universal)…')
#         self._run_cmd(['clean'])
#         self._run_cmd(['sdist', 'bdist_wheel'])
#         self.log.info('Uploading the package to PyPI via Twine…')
#         self._run(['twine', 'upload', 'dist/*'])
#         self.log.info('Pushing git tag…')
#         self._run(['git', 'tag', f"v{METADATA['version']}"])
#         self._run(['git', 'push', '--tags'])


def setup_package():
    """Create package setup information."""
    setup(
        name='innoconv',
        version=METADATA['version'],
        author=METADATA['author'],
        author_email=METADATA['author_email'],
        # cmdclass={
        #     'upload': UploadCommand,
        # },
        description=METADATA['description'],
        entry_points={
            'console_scripts': [
                'innoconv = innoconv.cli:cli',
            ],
        },
        extras_require={
            'doc': [
                'sphinx-click',
                'sphinx-rtd-theme',
                'Sphinx',
            ],
            'lint': [
                'flake8',
                'mccabe',
                'pydocstyle',
                'pylint',
            ],
            'test': [
                'coverage',
                'green',
            ],
        },
        include_package_data=True,
        install_requires=[
            'click>=7,<8',
            'PyYAML>=3.13,<4',
        ],
        packages=find_packages(exclude=[
            'test',
            'test.*',
            'integration_test',
            'integration_test.*',
        ]),
        python_requires='>=3.4.0',
        keywords=['innodoc', 'pandoc', 'markdown', 'education'],
        license=METADATA['license'],
        long_description=LONG_DESCRIPTION,
        long_description_content_type='text/markdown',
        url=METADATA['url'],
        zip_safe=False,
        project_urls={
            'Documentation': 'https://readthedocs.org/projects/innoconv/',
        },
        classifiers=[
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: ' +
            'GNU General Public License v3 or later (GPLv3+)',
            'Operating System :: POSIX :: Linux',
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Intended Audience :: Education',
            'Topic :: Education',
            'Topic :: Text Processing :: Markup',
        ],
    )


if __name__ == '__main__':
    try:
        setup_package()
    except RuntimeError as err:
        print(err)
        sys.exit(-1)
