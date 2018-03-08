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


def log(msg_string, level='INFO'):
    """Log messages for panzer.

    :param msg_string: Message that is logged
    :type msg_string: str
    :param level: Log level (``INFO``, ``WARNING``, ``ERROR`` OR ``CRITICAL``)
    :type level: str
    """
    msg = {
        'level': level,
        'message': msg_string,
    }
    pf.debug(json.dumps(msg))


def parse_fragment(parse_string):
    """Parse a source fragment using panzer.

    :param parse_string: Source fragment
    :type parse_string: str

    :rtype: list
    :returns: list of :class:`panflute.base.Element`
    :raises OSError: if panzer executable is not found
    :raises RuntimeError: if panzer recursion depth is exceeded
    :raises RuntimeError: if panzer output could not be parsed
    """

    panzer_bin = which('panzer')
    if panzer_bin is None or not os.path.exists(panzer_bin):
        err_msg = 'panzer executable not found!'
        log(err_msg, level='CRITICAL')
        raise OSError(err_msg)

    root_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
    panzer_cmd = [
        panzer_bin,
        '---panzer-support', os.path.join(root_dir, '.panzer'),
        '--from=latex+raw_tex',
        '--to=json',
        '--metadata=style:innoconv',
    ]

    # pass nesting depth as ENV var
    recursion_depth = int(os.getenv('INNOCONV_RECURSION_DEPTH', '0'))
    env = os.environ.copy()
    env['INNOCONV_RECURSION_DEPTH'] = str(recursion_depth + 1)

    if recursion_depth > 10:
        raise RuntimeError("Panzer recursion depth exceeded!")

    proc = Popen(panzer_cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, env=env)
    out, err = proc.communicate(input=parse_string.encode('utf-8'))

    if proc.returncode != 0:
        log('panzer process exited with non-zero return code.', level='ERROR')
        return []

    # only print filter messages for better output log
    match = REGEX_PATTERNS['PANZER_OUTPUT'].search(err.decode('utf-8'))
    if match:
        for line in match.group('messages').strip().splitlines():
            msg = u'↳ ' * recursion_depth + line.strip()
            log(msg, level='INFO')
    else:
        raise RuntimeError("Unable to parse panzer output!")

    doc = json.loads(out.decode('utf-8'), object_pairs_hook=from_json)
    return doc.content.list


def destringify(string):
    """Takes a string and transforms it into list of Str and Space objects.

    This function breaks down strings with whitespace. It could be done by
    calling :func:`parse_fragment` but doesn't have the overhead involed.

    :Example:

        >>> destringify('foo  bar\tbaz')
        [Str(foo), Space, Str(bar), Space, Str(baz)]

    :param string: String to transform
    :type string: str

    :rtype: list
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

    :param text: String to parse
    :type text: str

    :rtype: (str, list)
    :returns: command name and list of command arguments
    """
    match = REGEX_PATTERNS['CMD'].match(text)
    if not match:
        raise ParseError("Could not parse LaTeX command: '%s'" % text)
    cmd_name = match.groups()[0]
    cmd_args = re.findall(REGEX_PATTERNS['CMD_ARGS'], text)
    return cmd_name, cmd_args
