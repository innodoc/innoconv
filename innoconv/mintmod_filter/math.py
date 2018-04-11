"""Handle mintmod math commands."""

import re
from innoconv.constants import REGEX_PATTERNS
from innoconv.utils import parse_nested_args


MATH_SUBSTITUTIONS = (
    # leave \Rightarrow, ... intact
    (r'\\([NZQRC])($|[_\\$:=\s^,.])', r'\mathbb{\1}\2'),

    (r'\\Mtfrac', r'\\tfrac'),
    (r'\\Mdfrac', r'\\dfrac'),
    (r'\\MBlank', r'\ '),
    (r'\\MCondSetSep', r'{\,}:{\,}'),
    (r'\\MDFPSpace', r'\,'),
    (r'\\MDFPaSpace', r'\,\,'),
    (r'\\MDFPeriod', r'\, .'),
    (r'\\MSetminus', r'\setminus'),
    (r'\\MElSetSep', ';'),
    (r'\\MIntvlSep', ';'),
    (r'\\MEU', 'e'),
    (r'\\MDwSp', r'\,d'),
    (r'\\ML', 'L'),
    (r'\\MEmptyset', r'\emptyset'),
    (r'\\MUnderset', r'\underset'),
    (r'\\MBinom', r'\\binom'),
    (r'\\MTextSF', r'\\textsf'),
    (r'\\MHDots', r'\\dots'),

    (r'\\MSep', r'\\left\|{\\phantom{\\frac1g}}\\right.'),
    (r'\\MGrad', r'^{\\circ}'),

    (r'\\MGeoAbstand{([A-Za-z0-9])}{([A-Za-z0-9])}', r'[\\overline{\1\2}]'),
    (r'\\MGeoStrecke{([A-Za-z0-9])}{([A-Za-z0-9])}', r'\\overline{\1\2}'),
    (r'\\MGeoGerade{([A-Za-z0-9])}{([A-Za-z0-9])}', r'\1\2'),
    (r'\\MGeoDreieck{([A-Za-z0-9])}{([A-Za-z0-9])}{([A-Za-z0-9])}', r'\1\2\3'),

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

    # preprocess '\MPointTwo[\Big]{}{}' -> '\MPointTwo{\Big}{}{}'
    (r'\\MPointTwo\[([^]]+)\]', r'\\MPointTwo{\1}'),
)


def _handle_irregular(cmd_name, cmd_args):
    if cmd_name == 'MVector':
        ret = r'\begin{{pmatrix}}{}\end{{pmatrix}}'.format(*cmd_args)
    elif cmd_name == 'MPointTwo':
        if len(cmd_args) == 3:  # \Big variant
            ret = r'{0}({1}\coordsep {2}{{}}{0})'.format(*cmd_args)
        else:
            ret = r'({0}\coordsep {1})'.format(*cmd_args)
    elif cmd_name == 'MPointTwoAS':
        ret = r'\left({}\coordsep {}\right)'.format(*cmd_args)
    elif cmd_name == 'MPointThree':
        ret = r'({}\coordsep {}\coordsep {})'.format(*cmd_args)
    return ret


def handle_math(elem):
    """Handle mintmod text substitutions and some commands with irregular
    arguments."""
    for repl in MATH_SUBSTITUTIONS:
        elem.text = re.sub(repl[0], repl[1], elem.text)

    if not REGEX_PATTERNS['IRREG_MATH_CMDS'].search(elem.text):
        return elem

    # commands with arguments that may contain nested arguments (can't be
    # handled by regex)
    text = ''
    rest = elem.text
    while rest:
        match = REGEX_PATTERNS['IRREG_MATH_CMDS'].search(rest)
        if match:
            cmd_name = match.group()
            start = match.start()
            text += rest[:start]
            args_til_end = rest[start + len(cmd_name):]
            cmd_args, rest = parse_nested_args(args_til_end)
            text += _handle_irregular(cmd_name[1:], cmd_args)
        else:
            text += rest
            rest = None
    elem.text = text
    return elem
