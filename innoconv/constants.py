"""All project constants are defined here."""

import re

# regex patterns
REGEX_PATTERNS = {
    'CMD': re.compile(r'\\([^\\\s{]+)', re.DOTALL),
    'CMD_ARGS': re.compile(r'{([^}]+)}'),
    'ENV': re.compile(r'\A\\begin{(?P<env_name>[^}]+)}(.+)'
                      r'\\end{(?P=env_name)}\Z', re.DOTALL),
    'ENV_ARGS': re.compile(
        r'\A{(?P<arg>[^\n\r}]+)}(?P<rest>.+)\Z', re.DOTALL),
}

# element classes
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
    'UNKNOWN_CMD': ['unknown-command'],
    'UNKNOWN_ENV': ['unknown-environment'],
}

# colors
COLORS = {
    'UNKNOWN_CMD': '#ffa500',
    'UNKNOWN_ENV': '#ff4d00',
}
