#!/usr/bin/env python3
# pylint: disable=missing-docstring

"""Define project commands."""
import os
import logging
import re
import sys
from setuptools import setup, find_packages

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

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


def setup_package():
    setup(
        name='innoconv',
        version=METADATA['version'],
        author=METADATA['author'],
        author_email=METADATA['author_email'],
        description='Converter for interactive educational content.',
        entry_points={
            'console_scripts': [
                'innoconv = innoconv.__main__:main',
            ],
        },
        include_package_data=True,
        install_requires=[],
        packages=find_packages(exclude=["*.test.*", "*.test"]),
        python_requires='>=3',
        keywords=['innodoc', 'pandoc', 'markdown', 'education'],
        license=METADATA['license'],
        long_description=LONG_DESCRIPTION,
        long_description_content_type='text/markdown',
        url=METADATA['url'],
        zip_safe=False,
        project_urls={
            'Documentation': 'https://readthedocs.org/projects/innoconv/',
            'Source': 'https://gitlab.tu-berlin.de/innodoc/innoconv',
        },
        classifiers=(
            "Programming Language :: Python :: 3.6",
            "License :: OSI Approved :: " +
            "GNU General Public License v3 or later (GPLv3+)",
            "Operating System :: POSIX :: Linux",
            "Development Status :: 3 - Alpha",
            "Environment :: Console",
            "Intended Audience :: Education",
            "Topic :: Education",
            "Topic :: Text Processing :: Markup",
        ),
    )


if __name__ == '__main__':
    try:
        setup_package()
    except RuntimeError as err:
        get_logger().error('%s: %s', type(err).__name__, err)
        sys.exit(-1)
