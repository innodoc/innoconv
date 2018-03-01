"""Utility Module."""

import os
import json
import re
from subprocess import Popen, PIPE
from shutil import which
import panflute as pf
from panflute.elements import from_json

from innoconv.constants import REGEX_PATTERNS
from innoconv.errors import ParseError


def debug(msg, *args, **kwargs):
    """Print debug message."""
    pf.debug('[MINTMOD] %s' % msg, *args, **kwargs)


def debug_nested(msg, *args, **kwargs):
    """Print debug message for a nested filter instance."""
    # only print message if not empty strip returns false for strings that only
    # consist of whitespace characters
    if msg and msg.strip():
        pf.debug(u'↳ %s' % msg, *args, **kwargs)


def pandoc_parse(parse_string):
    """Parse ``parse_string`` using Pandoc and this filter.

    The panflute helper function ``convert_text`` does not print debug
    messages. So we have our own version.
    """

    def filter_path(filter_name):
        """Return path for filter main entry point."""
        return os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            filter_name, '__main__.py')

    args = [
        '--from=latex+raw_tex', '--to=json',
        # TODO: enable ifttm_filter
        # '--filter=%s' % filter_path('ifttm_filter'),
        '--filter=%s' % filter_path('mintmod_filter'),
    ]
    out, err = run_pandoc(parse_string, args)
    if err is not None:
        debug_nested(fix_line_endings(err))
    if out is not None:
        out = fix_line_endings(out)
        out = json.loads(out, object_pairs_hook=from_json)
        out = out.content.list
        return out
    return []


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
        debug('Pandoc process exited with non-zero return code.')
        debug('-- BEGIN of Pandoc output --')
        debug_nested(fix_line_endings(err))
        debug('-- END of Pandoc output --')
        return None, None
    return out.decode('utf-8'), err.decode('utf-8')


def fix_line_endings(repl):
    r"""Replace \r\n with \n."""
    if isinstance(repl, bytes):
        repl = str(repl, 'utf-8')
    return "\n".join(repl.splitlines())


def destringify(string):
    """Takes a string and transforms it into list of Str and Space objects.

    This function breaks down strings with whitespace. It could be done by
    calling :func:`pandoc_parse` but doesn't have the overhead involed.

    :Example:

        >>> destringify('foo  bar\tbaz')
        [Str(foo), Space, Str(bar), Space, Str(baz)]

    :param string: String to transform
    :type string: str

    :returns: list of :class:`panflute.Str` and :class:`panflute.Space`
    """
    ret = []
    split = string.split()
    for word in split:
        ret.append(pf.Str(word))
        if split.index(word) != len(split) - 1:
            ret.append(pf.Space())
    return ret


def parse_cmd(text):
    r"""
    Parse a LaTeX command using regular expressions.

    Parses a command like: ``\foo{bar}{baz}``

    :param string: String to parse
    :type string: str

    :returns: `str` cmd_name, list of `str` cmd_args
    """
    match = REGEX_PATTERNS['CMD'].match(text)
    if not match:
        raise ParseError("Could not parse LaTeX command: '%s'" % text)
    cmd_name = match.groups()[0]
    cmd_args = re.findall(REGEX_PATTERNS['CMD_ARGS'], text)
    return cmd_name, cmd_args