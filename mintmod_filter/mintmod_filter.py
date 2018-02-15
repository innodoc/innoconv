"""The actual filter function."""

import sys
import os
import re
import panflute as pf
from slugify import slugify

MATH_REPL = (
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

class ParseError(ValueError):
    """Is raised when mintmod commands could not be parsed."""
    pass

PATTERN_SPECIAL = re.compile(r'\\special{html:(.*)}')
PATTERN_MSECTION = re.compile(r'\\MSection{([^}]*)}')
PATTERN_ENV = re.compile(r'\A\\begin{(?P<env_name>[^}]+)}(.+)\\end{(?P=env_name)}\Z', re.DOTALL)
PATTERN_ENV_ARGS = re.compile(r'\A{(?P<arg>[^\n\r}]+)}(?P<rest>.+)\Z', re.DOTALL)

def debug(msg, *args, **kwargs):
    """Print preprocessor debug message."""
    pf.debug('[MINTMOD] %s' % msg, *args, **kwargs)

def error(msg, *args, **kwargs):
    """Print error and exit."""
    pf.debug('[MINTMOD] ERROR: %s' % msg, *args, **kwargs)
    sys.exit(-1)

def debug_elem(elem):
    """Print debug info about element."""
    debug('Element debug (%s)' % type(elem))
    debug(elem)

def pandoc_parse(parse_string):
    """Parse `parse_string` using Pandoc and this filter."""
    filter_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), '__main__.py')
    return pf.convert_text(
        parse_string, input_format='latex',
        extra_args=['--filter=%s' % filter_path]
    )

def handle_cmd_special(elem):
    r"""Handle LaTeX command \special. It's commonly used to embed HTML code.
    We parse the HTML and insert it.
    """
    match = PATTERN_SPECIAL.match(elem.text)
    if match:
        return pf.RawBlock(match.groups()[0])
    debug(r'Could not find HTML in \special: %s' % elem.text)
    return elem

def handle_cmd_msection(elem, doc):
    """Remember MSection name for later"""
    match = PATTERN_MSECTION.search(elem.text)
    if match is None:
        raise ParseError(r'Could not \MSection: %s' % elem)
    doc.msection_content = match.groups()[0]
    doc.msection_id = slugify(match.groups()[0])
    return []

def handle_environment(elem, doc):
    """Parse and handle mintmod environments"""
    match = PATTERN_ENV.search(elem.text)
    if match is None:
        raise ParseError('Could not parse environment: %s...' % elem.text[:50])

    env_name = match.group('env_name')
    inner_code = match.groups()[1]

    # Parse optional arguments
    env_args = []
    rest = inner_code
    while True:
        match = PATTERN_ENV_ARGS.search(rest)
        if match is None:
            break
        env_args.append(match.group('arg'))
        rest = match.group('rest')

    # Handle different environments
    if env_name == 'MSectionStart':
        # Use title from previously found \MSection command
        header = pf.Header(
            pf.RawInline(doc.msection_content),
            identifier=doc.msection_id, level=2
        )
        div = pf.Div(classes=['section-start'])
        div.content.extend([header] + pandoc_parse(rest))
        return div

    elif env_name == 'MXContent':
        title = env_args[0]
        header = pf.Header(
            pf.RawInline(title), identifier=slugify(title), level=3)
        div = pf.Div(classes=['content'])
        div.content.extend([header] + pandoc_parse(rest))
        return div

    return elem

def mintmod_filter(elem, doc):
    """Main entry point for doc.walk."""
    if isinstance(elem, pf.Math):
        for repl in MATH_REPL:
            elem.text = elem.text.replace(repl[0], repl[1])
        return elem
    elif isinstance(elem, pf.RawBlock) and elem.format == 'latex':
        # handle mintmod commands
        if elem.text.startswith(r'\MSection{'):
            return handle_cmd_msection(elem, doc)
        elif elem.text.startswith(r'\begin{'):
            return handle_environment(elem, doc)
        # handle mintmod environments
        elif elem.text.startswith(r'\special'):
            return handle_cmd_special(elem)
        else:
            debug('Unhandled RawBlock: %s' % elem.text)
    return None
