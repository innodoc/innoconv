"""Project constants are defined here."""

from collections import OrderedDict
import re
import os


#: Element class for index labels
INDEX_LABEL_PREFIX = 'index-label'

#: Don't show this unknown commands/envs in error log
EXERCISE_CMDS_ENVS = (
    'MLParsedQuestion', 'MLSimplifyQuestion', 'MLFunctionQuestion',
    'MDirectRouletteExercises', 'MSetPoints', 'MLCheckbox',
    'MLIntervalQuestion', 'MGroupButton', 'MLQuestion', 'MExerciseCollection',
    'MQuestionGroup', 'MLSpecialQuestion',
)

# These values mirror the values set in
# https://gitlab.tu-berlin.de/innodoc/innodoc-webapp/blob/master/lib/questionTypes.js
QUESTION_TYPES = {
    'EXACT': 'exact',
    'MATH_EXPRESSION': 'mathExpression',
    'MATH_FORMULA': 'mathFormula',
    'MATH_SIMPLIFY': 'mathSimplify',
    'SPECIAL': 'special',
    'BOOLEAN': 'boolean',
    'MATH_INTERVAL': 'mathInterval'
}

#: Simple Regex substitutions for math
MATH_SUBSTITUTIONS = (
    # leave \Rightarrow, ... intact
    (r'\\([NZQRC])($|[_\\$:=\s^,.})])', r'\mathbb{\1}\2'),

    (r'\\Mtfrac', r'\\tfrac'),
    (r'\\Mdfrac', r'\\dfrac'),
    (r'\\MBlank', r'\ '),
    (r'\\MCondSetSep', r' {\,}:{\,}'),
    (r'\\MDFPSpace', r'\,'),
    (r'\\MDFPaSpace', r'\,\,'),
    (r'\\MDFPeriod', r'\, .'),
    (r'\\MTSP', r''),
    (r'\\MSetminus', r'\setminus'),
    (r'\\MElSetSep', ';'),
    (r'\\MIntvlSep', ';'),
    (r'\\MEU', 'e'),
    (r'\\MDwSp', r'\,d'),
    (r'\\ML', ' L'),
    (r'\\MEmptyset', r'\emptyset'),
    (r'\\MUnderset', r'\underset'),
    (r'\\MBinom', r'\\binom'),
    (r'\\MTextSF', r'\\textsf'),
    (r'\\MHDots', r'\\dots'),
    (r'\\Mvarphi', r'\\varphi'),
    (r'\\MDFPeriod', r'\, .'),
    (r'\\Mmeasuredangle', r'\\measuredangle'),
    (r'\\lto', r'\\longrightarrow'),
    (r'\\null', r''),
    (r'\\MOhm', r'\\Omega'),
    (r'\\Mvarepsilon', r'\\varepsilon'),
    (r'\\ld\(', r'\\mathrm{ld}('),
    (r'\\MGGT', r'\\mathrm{ggT}'),

    (r'\\MSep', r'\\left\|{\\phantom{\\frac1g}}\\right.'),
    (r'\\MGrad', r'^{\\circ}'),

    (r'\\MGeoAbstand{([A-Za-z0-9])}{([A-Za-z0-9])}', r'[\\overline{\1\2}]'),
    (r'\\MGeoStrecke{([A-Za-z0-9])}{([A-Za-z0-9])}', r'\\overline{\1\2}'),
    (r'\\MGeoGerade{([A-Za-z0-9])}{([A-Za-z0-9])}', r'\1\2'),
    (r'\\MGeoDreieck{([A-Za-z0-9])}{([A-Za-z0-9])}{([A-Za-z0-9])}', r'\1\2\3'),

    (r'\\Id\((.*?)\)', r'\\operatorname{Id}(\1)'),
    (r'\\Id', r'\\mathrm{Id}'),
    (r'\\Mid', r'\\mathrm{id}'),

    (r'\\MRelates', r'\\stackrel{\\scriptscriptstyle\\wedge}{=}'),
    (r'\\Mmapsto', r'\\mapsto'),

    # handled by innoconv.mathjax.js
    (r'\\MZahl{([0-9]+?)}{([0-9]*?)}', r'\\num{\1.\2}'),
    (r'\\MZXYZhltrennzeichen}', r'\decmarker'),

    # intervals (#17)
    (r'\\MoIl\[\\left\]', r'\left]'),
    (r'\\MoIr\[\\right\]', r'\\right['),
    (r'\\MoIl', ']'),
    (r'\\MoIr', '['),

    # vectors
    (r'\\MDVec', r'\\overrightarrow'),
    (r'\\MVec{', r'\\vec{'),  # trailing '{' so it doesn't touch \MVector

    # italic integral
    (r'\\MD', r'd'),

    # MCaseEnv
    (r'\\begin{MCaseEnv}', r'\\left\\lbrace\\begin{array}{rl}'),
    (r'\\end{MCaseEnv}', r'\\end{array}\\right.'),

    # preprocess '\MPointTwo[\Big]{}{}' -> '\MPointTwo{\Big}{}{}'
    (r'\\MPoint(Two|Three)\[([^]]+)\]', r'\\MPoint\1{\2}'),

    # preprocess '\MEinheit[]' -> '\MEinheit{}'
    (r'\\MEinheit\[\]', r'\\MEinheit{}'),
)

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

    'MATH_MCASEENV': re.compile('\begin{MCaseEnv}'),
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
    'MGROUPBUTTON': ['verify-input-button'],
    'MQUESTIONGROUP': ['question-group'],
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

#: Default innoconv input format
DEFAULT_INPUT_FORMAT = 'latex+raw_tex'

#: Output format choices
INPUT_FORMAT_CHOICES = (
    'latex+raw_tex',
    'markdown',
)

#: project root dir
ROOT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')

#: panzer support directory
PANZER_SUPPORT_DIR = os.path.join(ROOT_DIR, '.panzer')

#: timeout for panzer child-process (in seconds)
PANZER_TIMEOUT = 1800

#: encoding used in this project
ENCODING = 'utf-8'

#: Translatable strings
TRANSLATIONS = {
    'introduction': {
        'de': 'Einführung',
        'en': 'Introduction',
    },
}
