"""Project constants."""

import os


#: Default innoconv output directory
DEFAULT_OUTPUT_DIR_BASE = os.path.join(".", "innoconv_output")

#: Default enabled extensions
DEFAULT_EXTENSIONS = (
    "copy_static",
    "generate_toc",
    "join_strings",
    "tikz2svg",
    "write_manifest",
)

#: Encoding used in this project
ENCODING = "utf-8"

#: Basename for the content file in a section
CONTENT_BASENAME = "content"

#: Manifest filename
MANIFEST_BASENAME = "manifest"

#: Format for logger messages
LOG_FORMAT = "%(levelname)s:%(filename)s %(message)s"

#: Static folder name
STATIC_FOLDER = "_static"

#: CLI exit codes
EXIT_CODES = {"SUCCESS": 0, "MANIFEST_ERROR": 10, "RUNNER_ERROR": 11}
