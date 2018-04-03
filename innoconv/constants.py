"""Project constants are defined here."""

import re
import os


#: Regular expressions
REGEX_PATTERNS = {
    # latex parsing
    'CMD': re.compile(r'\A\\([^\\\s{]+)(.*)\Z', re.DOTALL),
    'ENV': re.compile(r'\A\\begin{(?P<env_name>[^}]+)}(.+)'
                      r'\\end{(?P=env_name)}\Z', re.DOTALL),
    'ENV_ARGS': re.compile(
        r'\A{(?P<arg>[^\n\r}]+)}(?P<rest>.+)\Z', re.DOTALL),

    # panzer output parsing
    'PANZER_OUTPUT':
        re.compile(r"----- run list -----.+? json(?:\n|\r\n?)(?P<messages>.+)"
                   "----- pandoc write -----", re.MULTILINE | re.DOTALL)
}

#: Element classes
ELEMENT_CLASSES = {
    'IMAGE': ['img'],
    'DEBUG_UNKNOWN_CMD': ['innoconv-debug-unknown-command'],
    'DEBUG_UNKNOWN_ENV': ['innoconv-debug-unknown-environment'],
    'MXCONTENT': ['content'],
    'MINTRO': ['content', 'intro'],
    'MEXERCISES': ['content', 'exercises'],
    'MEXERCISE': ['panel', 'panel-default', 'exercise'],
    'MINFO': ['panel', 'panel-info', 'info'],
    'MEXPERIMENT': ['panel', 'panel-default', 'experiment'],
    'MEXAMPLE': ['panel', 'panel-default', 'example'],
    'MHINT': ['panel', 'panel-default', 'hint'],
    'MINPUTHINT': ['hint-text'],
    'MSECTIONSTART': ['section-start'],
    'MYOUTUBE_VIDEO': ['video', 'video-youtube'],
}

#: Supported language codes
LANGUAGE_CODES = (
    'de',
    'en',
)

#: Default language code
DEFAULT_LANGUAGE_CODE = LANGUAGE_CODES[0]

#: Default innoconv output directory
DEFAULT_OUTPUT_DIR_BASE = os.path.join(os.getcwd(), 'innoconv_output')

#: Default innoconv output format
DEFAULT_OUTPUT_FORMAT = 'json'

#: mapping between output formats and file extensions
OUTPUT_FORMAT_EXT_MAP = {
    'html5': 'html',
    'json': 'json',
    'latex': 'tex',
    'markdown': 'md',
    'asciidoc': 'adoc',
}

#: Output format choices
OUTPUT_FORMAT_CHOICES = list(OUTPUT_FORMAT_EXT_MAP.keys())

#: project root dir
ROOT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')

#: panzer support directory
PANZER_SUPPORT_DIR = os.path.join(ROOT_DIR, '.panzer')

#: encoding
ENCODING = 'utf-8'
