"""Handle mintmod math commands."""

import re
from innoconv.constants import REGEX_PATTERNS, COMMANDS_IRREGULAR
from innoconv.utils import parse_nested_args, log


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

    # preprocess '\MPointTwo[\Big]{}{}' -> '\MPointTwo{\Big}{}{}'
    (r'\\MPoint(Two|Three)\[([^]]+)\]', r'\\MPoint\1{\2}'),

    # preprocess '\MEinheit[]' -> '\MEinheit{}'
    (r'\\MEinheit\[\]', r'\\MEinheit{}'),
)


def handle_math(elem):
    """Handle mintmod text substitutions and some commands with irregular
    arguments."""
    for repl in MATH_SUBSTITUTIONS:
        elem.text = re.sub(repl[0], repl[1], elem.text)

    if REGEX_PATTERNS['IRREG_MATH_CMDS'].search(elem.text):
        def _handle_irregular(cmd_name, cmd_args):
            sub = COMMANDS_IRREGULAR[cmd_name]
            if isinstance(sub, dict):
                try:
                    sub = sub[len(cmd_args)]
                except KeyError:
                    log('Could not find substitution for this number of args: '
                        '{} ({})'.format(cmd_name, cmd_args))
                    raise
            try:
                return sub.format(*cmd_args)
            except IndexError:
                log('Received wrong number of arguments for math command: '
                    '{} ({})'.format(cmd_name, cmd_args))
                raise

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
