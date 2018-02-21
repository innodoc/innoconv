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
    # only print message if not empty strip returns false for strings that only
    # consist of whitespace characters
    if msg and msg.strip():
        pf.debug('[nested] %s' % msg, *args, **kwargs)


def pandoc_parse(parse_string):
    """Parse ``parse_string`` using Pandoc and this filter.

    The panflute helper function ``convert_text`` does not print debug
    messages. So we have our own version.
    """
    filter_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), '__main__.py')

    args = ['--from=latex+raw_tex', '--to=json', '--filter=%s' % filter_path]
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
    if type(repl) == bytes:
        repl = str(repl, 'utf-8')
    return "\n".join(repl.splitlines())
