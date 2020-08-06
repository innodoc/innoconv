"""Project constants."""

import os


#: Allowed section types
ALLOWED_SECTION_TYPES = ("exercises", "test")

#: Default innoconv output directory
DEFAULT_OUTPUT_DIR_BASE = os.path.join(".", "innoconv_output")

#: Default enabled extensions
DEFAULT_EXTENSIONS = (
    "copy_static",
    "generate_toc",
    "index_terms",
    "join_strings",
    "number_boxes",
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

#: Allowed file extensions for course logo
LOGO_EXTENSIONS = ("png", "jpg", "jpeg", "gif", "svg")

#: Static folder name
STATIC_FOLDER = "_static"

#: Custom content folder name
PAGES_FOLDER = "_pages"

#: Prefix for footer fragment files
FOOTER_FRAGMENT_PREFIX = "_footer_"

#: CLI exit codes
EXIT_CODES = {"SUCCESS": 0, "MANIFEST_ERROR": 10, "RUNNER_ERROR": 11}
