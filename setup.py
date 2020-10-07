#!/usr/bin/env python3
"""setuptools packaging."""

import os
import re
import sys

from setuptools import setup

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))

# Need to parse metadata manually as setup.py must not import innoconv
METADATA_PATH = os.path.join(ROOT_DIR, "innoconv", "metadata.py")
with open(METADATA_PATH, "r") as metadata_file:
    METADATA = dict(
        re.findall(r"__([a-z_]+)__\s*=\s*['\"]([^'\"]+)['\"]", metadata_file.read())
    )


with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()


def setup_package():
    """Create package setup information."""
    setup(
        name="innoconv",
        version=METADATA["version"],
        author=METADATA["author"],
        author_email=METADATA["author_email"],
        description=METADATA["description"],
        entry_points={"console_scripts": ["innoconv = innoconv.cli:cli"]},
        include_package_data=True,
        install_requires=[
            "click>=7,<8",
            "coloredlogs>=14,<15",
            "python-slugify>=4,<5",
            "PyYAML>=5,<6",
        ],
        packages=["innoconv", "innoconv.ext"],
        python_requires=">=3.6.0",
        keywords=["innodoc", "pandoc", "markdown", "education"],
        license=METADATA["license"],
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/markdown",
        url=METADATA["url"],
        zip_safe=False,
        project_urls={"Documentation": "https://readthedocs.org/projects/innoconv/"},
        classifiers=[
            "Development Status :: 4 - Beta",
            "Environment :: Console",
            "Intended Audience :: Education",
            "Intended Audience :: End Users/Desktop",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved"
            " :: GNU General Public License v3 or later (GPLv3+)",
            "Operating System :: POSIX :: Linux",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3 :: Only",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Topic :: Education",
            "Topic :: Text Processing :: Markup",
            "Topic :: Scientific/Engineering",
        ],
    )


if __name__ == "__main__":
    try:
        setup_package()
    except RuntimeError as err:
        print(err)
        sys.exit(-1)
