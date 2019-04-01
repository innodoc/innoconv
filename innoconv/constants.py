"""Project constants."""

import os


#: Default innoconv output directory
DEFAULT_OUTPUT_DIR_BASE = os.path.join(".", "innoconv_output")

#: Default enabled extensions
DEFAULT_EXTENSIONS = (
    "join_strings",
    "copy_static",
    "generate_toc",
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
