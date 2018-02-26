"""Handle mintmod text substitution commands."""

MATH_SUBSTITUTIONS = (
    (r'\N', r'\mathbb{N}'),
    (r'\Z', r'\mathbb{Z}'),
    (r'\Q', r'\mathbb{Q}'),
    (r'\R', r'\mathbb{R}'),
    (r'\C', r'\mathbb{C}'),
    (r'\Mtfrac', r'\tfrac'),
    (r'\Mdfrac', r'\dfrac'),
    (r'\MBlank', r'\ '),
    (r'\MCondSetSep', r'{\,}:{\,}'),
)


def handle_math_substitutions(elem):
    """Handle simple mintmod text substitutions in math environments."""
    for repl in MATH_SUBSTITUTIONS:
        elem.text = elem.text.replace(repl[0], repl[1])
    return elem
