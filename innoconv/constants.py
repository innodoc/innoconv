"""Project constants are defined here."""

from collections import OrderedDict
import re
import os


#: Element class for index labels
INDEX_LABEL_PREFIX = 'index-label'

#: Math commands with irregular arguments, key=command-name,
#: value=formatstring or value=dict (number of arguments, formatstring)
COMMANDS_IRREGULAR = OrderedDict((
    ('MVector', r'\begin{{pmatrix}}{}\end{{pmatrix}}'),
    ('MPointTwoAS', r'\left({}\coordsep {}\right)'),
    (
        'MPointTwo', {
            2: r'({0}\coordsep {1})',
            3: r'{0}({1}\coordsep {2}{{}}{0})',
        }
    ),
    (
        'MPointThree', {
            3: r'({}\coordsep {}\coordsep {})',
            4: r'{0}({1}\coordsep {2}\coordsep {3}{{}}{0})',
        }
    ),
    (
        'MCases',
        r'\left\lbrace{{\begin{{array}}{{rl}} {} \end{{array}}}}\right.',
    ),
    (
        'function',
        r'{}:\;\left\lbrace{{\begin{{array}}{{rcl}} {} '
        r'&\longrightarrow & {} \\ {} &\longmapsto  '
        r'& {} \end{{array}}}}\right.',
    ),
    (
        'MEinheit', {
            1: r'\, \mathrm{{{}}}',
            2: r'\mathrm{{{1}}}',
        },
    ),
))

#: Regular expressions
REGEX_PATTERNS = {
    # latex parsing
    'CMD': re.compile(r'\A\\([^\\\s{]+)(.*)\Z', re.DOTALL),
    'ENV': re.compile(r'\A\\begin{(?P<env_name>[^}]+)}(.+)'
                      r'\\end{(?P=env_name)}\Z', re.DOTALL),

    'LABEL': re.compile(r'^{}-(.+)$'.format(INDEX_LABEL_PREFIX)),
    'STRIP_HASH_LINE': re.compile(r'^\%(\r\n|\r|\n)'),

    # panzer output parsing
    'PANZER_OUTPUT':
        re.compile(r"----- filter -----.+?json(?:\n|\r\n?)(?P<messages>.+)"
                   "----- pandoc write -----", re.MULTILINE | re.DOTALL),

    'FIX_MTEST': re.compile(
        r" (zu )?(Kapitel|Modul) (\d{1,2}|\\arabic{section})"),

    'IRREG_MATH_CMDS':
        re.compile('({})'.format(
            '|'.join(r'\\{}'.format(cmd)
                     for cmd in list(COMMANDS_IRREGULAR.keys())))),
}

#: Element classes
ELEMENT_CLASSES = {
    'HIGHLIGHT': ['highlight'],
    'IMAGE': ['img'],
    'FIGURE': ['figure'],
    'DEBUG_UNKNOWN_CMD': ['innoconv-debug-unknown-command'],
    'DEBUG_UNKNOWN_ENV': ['innoconv-debug-unknown-environment'],
    'MCOSHZUSATZ': ['secondary'],
    'MEXAMPLE': ['example'],
    'MEXERCISE': ['exercise'],
    'MEXERCISES': ['exercises'],
    'MEXPERIMENT': ['experiment'],
    'MHINT': ['hint'],
    'MINFO': ['info'],
    'MINPUTHINT': ['hint-text'],
    'MINTRO': ['intro'],
    'MTEST': ['test'],
    'MTIKZAUTO': ['tikz'],
    'MVIDEO': ['video', 'video-static'],
    'MYOUTUBE_VIDEO': ['video', 'video-youtube'],
}

#: Subjects as used in mintmod command ``\MSetSubject``
MINTMOD_SUBJECTS = {
    r'\MINTMathematics': 'mathematics',
    r'\MINTInformatics': 'informatics',
    r'\MINTChemistry': 'chemistry',
    r'\MINTPhysics': 'physics',
    r'\MINTEngineering': 'engineering',
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

#: timeout for panzer child-process (in seconds)
PANZER_TIMEOUT = 1200

#: encoding used in this project
ENCODING = 'utf-8'
