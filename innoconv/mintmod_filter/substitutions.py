"""Handle mintmod text substitution commands."""

import re


MATH_SUBSTITUTIONS = (
    # leave \Rightarrow, ... intact
    (r'\\([NZQRC])($|[_\\$:=\s^,.])', r'\mathbb{\1}\2'),

    (r'\\Mtfrac{(.*?)}{(.*?)}', r'{\\textstyle \\frac{\1}{\2}}'),
    (r'\\Mdfrac{(.*?)}{(.*?)}', r'{\\displaystyle \\frac{\1}{\2}}'),
    (r'\\MBlank', r'\ '),
    (r'\\MCondSetSep', r'{\,}:{\,}'),
    (r'\\MDFPSpace', r'\,'),
    (r'\\MDFPaSpace', r'\,\,'),
    (r'\\MDFPeriod', r'\, .'),
    (r'\\MSetminus', r'\setminus'),
    (r'\\MElSetSep', ';'),
    (r'\\MIntvlSep', ';'),
    (r'\\MEU', 'e'),
    (r'\\MZahl{([0-9]*?)}{([0-9]*?)}', r'\1{,}\2'),  # maybe obsolete (see #16)

    # intervals (#17)
    (r'\\MoIl\[\\left\]', r'\left]'),
    (r'\\MoIr\[\\right\]', r'\\right['),
    (r'\\MoIl', ']'),
    (r'\\MoIr', '['),
)


def handle_math_substitutions(elem):
    """Handle simple mintmod text substitutions in math environments."""
    for repl in MATH_SUBSTITUTIONS:
        elem.text = re.sub(repl[0], repl[1], elem.text)
    return elem
