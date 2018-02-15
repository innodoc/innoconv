"""Utility Module."""

import os
import json
from subprocess import Popen, PIPE
from shutil import which

import panflute as pf
from panflute.elements import from_json


class ParseError(ValueError):
    """Is raised when mintmod commands could not be parsed."""

    pass


def debug(msg, *args, **kwargs):
    """Print debug message."""
    pf.debug('[MINTMOD] %s' % msg, *args, **kwargs)


def debug_nested(msg, *args, **kwargs):
    """Print debug message for a nested filter instance."""
    pf.debug('[nested] %s' % msg, *args, **kwargs)


def debug_elem(elem):
    """Print debug info about element."""
    debug('[MINTMOD] Element debug (%s)' % type(elem))
    debug(elem)


def pandoc_parse(parse_string):
    """Parse `parse_string` using Pandoc and this filter.

    The panflute helper function `convert_text` does not print debug messages.
    So we have our own version.
    """
    filter_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), '__main__.py')

    from_arg = '--from={}'.format('latex')
    to_arg = '--to={}'.format('json')
    args = [from_arg, to_arg, '--filter=%s' % filter_path]
    out, err = run_pandoc(parse_string, args)
    debug_nested(fix_line_endings(err))
    out = fix_line_endings(out)
    out = json.loads(out, object_pairs_hook=from_json)
    out = out.content.list
    return out


def run_pandoc(text='', args=None):
    """Call Pandoc with input text and/or arguments."""
    if args is None:
        args = []

    pandoc_path = which('pandoc')
    if pandoc_path is None or not os.path.exists(pandoc_path):
        raise OSError("Path to pandoc executable does not exists")

    proc = Popen([pandoc_path] + args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate(input=text.encode('utf-8'))
    exitcode = proc.returncode
    if exitcode != 0:
        raise IOError(err)
    return out.decode('utf-8'), err.decode('utf-8')


def fix_line_endings(_string):
    r"""Replace \r\n with \n."""
    return "\n".join(_string.splitlines())
