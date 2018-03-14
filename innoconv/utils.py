"""Utility module"""

import os
import json
import re
from shutil import which
from subprocess import Popen, PIPE
import sys

import panflute as pf
from panflute.elements import from_json

from innoconv.constants import REGEX_PATTERNS, ENCODING
from innoconv.errors import ParseError


def log(msg_string, level='INFO'):
    """Log messages when running as a panzer filter.

    :param msg_string: Message that is logged
    :type msg_string: str
    :param level: Log level (``INFO``, ``WARNING``, ``ERROR`` OR ``CRITICAL``)
    :type level: str
    """
    outgoing = {'level': level, 'message': msg_string}
    outgoing_json = json.dumps(outgoing) + '\n'
    if hasattr(sys.stderr, 'buffer'):
        outgoing_bytes = outgoing_json.encode(ENCODING)
        sys.stderr.buffer.write(outgoing_bytes)
    else:
        sys.stderr.write(outgoing_json)
    sys.stderr.flush()


def get_panzer_bin():
    """Get path of panzer binary."""
    panzer_bin = which('panzer')
    if panzer_bin is None or not os.path.exists(panzer_bin):
        raise OSError('panzer executable not found!')
    return panzer_bin


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

    root_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
    panzer_cmd = [
        get_panzer_bin(),
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
    # TODO: continuous log output
    out, err = proc.communicate(input=parse_string.encode(ENCODING))

    if proc.returncode != 0:
        log('panzer process exited with non-zero return code.', level='ERROR')
        return []

    # only print filter messages for better output log
    match = REGEX_PATTERNS['PANZER_OUTPUT'].search(err.decode(ENCODING))
    if match:
        for line in match.group('messages').strip().splitlines():
            log(u'↳ %s' % line.strip(), level='INFO')
    else:
        raise RuntimeError("Unable to parse panzer output!")

    doc = json.loads(out.decode(ENCODING), object_pairs_hook=from_json)
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
