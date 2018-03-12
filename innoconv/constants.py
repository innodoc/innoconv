"""Project constants are defined here."""

import re
import os


#: Regular expressions
REGEX_PATTERNS = {
    # latex parsing
    'CMD': re.compile(r'\\([^\\\s{]+)', re.DOTALL),
    'CMD_ARGS': re.compile(r'{([^}]+)}'),
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
    'MXCONTENT': ['content'],
    'MEXERCISES': ['content', 'exercises'],
    'MEXERCISE': ['exercise'],
    'MINFO': ['info'],
    'MEXPERIMENT': ['experiment'],
    'MEXAMPLE': ['example'],
    'MHINT': ['hint'],
    'MHINT_TEXT': ['hint-text'],
    'MSECTIONSTART': ['section-start'],
    'UNKNOWN_CMD': ['unknown-command'],
    'UNKNOWN_ENV': ['unknown-environment'],
    'MYOUTUBE_VIDEO': ['video', 'video-youtube']
}

#: Color codes
COLORS = {
    'UNKNOWN_CMD': '#ffa500',
    'UNKNOWN_ENV': '#ff4d00',
}

#: Supported language codes
LANGUAGE_CODES = (
    'de',
    'en',
)

#: Default language code
DEFAULT_LANGUAGE_CODE = LANGUAGE_CODES[0]

#: Default innoconv output directory
DEFAULT_OUTPUT_DIR = os.path.join(os.getcwd(), 'build')

#: project root dir
ROOT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')

#: panzer support directory
PANZER_SUPPORT_DIR = os.path.join(ROOT_DIR, '.panzer')
