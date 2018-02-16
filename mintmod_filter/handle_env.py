"""Handle mintmod LaTeX environments.

Convention: Provide a `handle_ENVNAME` function for handling `ENVNAME`
            environment. You need to slugify environment name.

Example: `handle_mxcontent` method will receive `MXContent` environment.
"""

import re
import panflute as pf
from slugify import slugify
from mintmod_filter.utils import debug, pandoc_parse, ParseError

PATTERN_ENV = re.compile(
    r'\A\\begin{(?P<env_name>[^}]+)}(.+)\\end{(?P=env_name)}\Z', re.DOTALL)
PATTERN_ENV_ARGS = re.compile(
    r'\A{(?P<arg>[^\n\r}]+)}(?P<rest>.+)\Z', re.DOTALL)

MXCONTENT_CLASSES = ['content']
MEXERCISES_CLASSES = ['content', 'exercises']
MEXERCISE_CLASSES = ['exercise']


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

    function_name = "handle_%s" % slugify(env_name)

    if function_name in globals():
        return globals()[function_name](rest, env_args, doc)

    debug("Could not handle environment %s." % env_name)
    return None


def handle_msectionstart(elem_content, env_args, doc):
    """Handle `MSectionStart` environment."""
    # Use title from previously found \MSection command
    header_title = getattr(doc, 'msection_content', "No Header Found")
    header_id = getattr(doc, 'msection_id', "no-id-found")
    header = pf.Header(
        pf.RawInline(header_title),
        identifier=header_id, level=2
    )
    div = pf.Div(classes=['section-start'])
    div.content.extend([header] + pandoc_parse(elem_content))
    return div


def handle_mxcontent(elem_content, env_args, doc):
    """Handle `MXContent` environment."""
    title = env_args[0]
    header = pf.Header(
        pf.RawInline(title), identifier=slugify(title), level=3)
    div = pf.Div(classes=MXCONTENT_CLASSES)
    div.content.extend([header] + pandoc_parse(elem_content))
    return div


def handle_mexercises(elem_content, env_args, doc):
    """Handle `MExercises` environment."""
    header = pf.Header(pf.RawInline('Aufgaben'), level=3)  # TODO i18n?
    div = pf.Div(classes=MEXERCISES_CLASSES)
    div.content.extend([header] + pandoc_parse(elem_content))
    return div


def handle_mexercise(elem_content, env_args, doc):
    """Handle `MExercise` environment."""
    header = pf.Header(pf.RawInline('Aufgabe'), level=4)  # TODO i18n?
    div = pf.Div(classes=MEXERCISE_CLASSES)
    div.content.extend([header] + pandoc_parse(elem_content))
    return div
