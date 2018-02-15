"""Module for handling latex environments."""

import re
import panflute as pf
from slugify import slugify
from mintmod_filter.utils import debug, pandoc_parse, ParseError

PATTERN_ENV = re.compile(
    r'\A\\begin{(?P<env_name>[^}]+)}(.+)\\end{(?P=env_name)}\Z', re.DOTALL)
PATTERN_ENV_ARGS = re.compile(
    r'\A{(?P<arg>[^\n\r}]+)}(?P<rest>.+)\Z', re.DOTALL)


def handle_environment(elem, doc):
    """Parse and handle mintmod environments."""
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

    function_name = "handle_env_%s" % slugify(env_name)

    if function_name in globals():
        return globals()[function_name](rest, env_args, doc)

    debug("Function %s not found" % function_name)
    return None


def handle_env_msectionstart(elem_content, env_args, doc):
    """Handle MSectionStart latex environments."""
    # Use title from previously found \MSection command
    header = pf.Header(
        pf.RawInline(doc.msection_content),
        identifier=doc.msection_id, level=2
    )
    div = pf.Div(classes=['section-start'])
    div.content.extend([header] + pandoc_parse(elem_content))
    return div


def handle_env_mxcontent(elem_content, env_args, doc):
    """Handle MXContent latex environments."""
    title = env_args[0]
    header = pf.Header(
        pf.RawInline(title), identifier=slugify(title), level=3)
    div = pf.Div(classes=['content'])
    div.content.extend([header] + pandoc_parse(elem_content))
    return div
