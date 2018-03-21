"""Handle mintmod text substitution commands."""

import re


MATH_SUBSTITUTIONS = (
    # leave \Rightarrow, ... intact
    (r'\\N($|[$^_,.\s])', r'\mathbb{N}\1'),
    (r'\\Z($|[$^_,.\s])', r'\mathbb{Z}\1'),
    (r'\\Q($|[$^_,.\s])', r'\mathbb{Q}\1'),
    (r'\\R($|[$^_,.\s])', r'\mathbb{R}\1'),
    (r'\\C($|[$^_,.\s])', r'\mathbb{C}\1'),

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
    (r'\\MoIl', ']'),  # (#17)
    (r'\\MoIr', '['),  # (#17)
    (r'\\MEU', 'e'),
    (r'\\MZahl{([0-9]*?)}{([0-9]*?)}', r'\1{,}\2')  # maybe obsolete (see #16)
)


def handle_math_substitutions(elem):
    """Handle simple mintmod text substitutions in math environments."""
    for repl in MATH_SUBSTITUTIONS:
        elem.text = re.sub(repl[0], repl[1], elem.text)
    return elem
