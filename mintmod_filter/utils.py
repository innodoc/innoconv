"""Utility Module."""

import re
import os
import panflute as pf


class ParseError(ValueError):
    """Is raised when mintmod commands could not be parsed."""

    pass


PATTERN_SPECIAL = re.compile(r'\\special{html:(.*)}')
PATTERN_MSECTION = re.compile(r'\\MSection{([^}]*)}')
PATTERN_ENV = re.compile(
    r'\A\\begin{(?P<env_name>[^}]+)}(.+)\\end{(?P=env_name)}\Z', re.DOTALL)
PATTERN_ENV_ARGS = re.compile(
    r'\A{(?P<arg>[^\n\r}]+)}(?P<rest>.+)\Z', re.DOTALL)


def debug(msg, *args, **kwargs):
    """Print preprocessor debug message."""
    pf.debug('[MINTMOD] %s' % msg, *args, **kwargs)


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
