"""Utility module"""

import json
from subprocess import Popen, PIPE
import sys

from innoconv.constants import ENCODING


def log(msg_string):
    """Log message to stderr.

    :param msg_string: Message that is logged
    :type msg_string: str
    """
    sys.stderr.write("{}\n".format(msg_string))
    sys.stderr.flush()


def to_ast(filepath):
    """Convert a file to abstract syntax tree using pandoc.

    :param filepath: Path of file
    :type filepath: str

    :rtype: list of dicts (pandoc elements)
    :returns: parsed elements

    :raises RuntimeError: if pandoc exits with an error
    """
    pandoc_cmd = ['pandoc', '--to=json', filepath]
    proc = Popen(pandoc_cmd, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate(timeout=60)
    out = out.decode(ENCODING)
    err = err.decode(ENCODING)

    if proc.returncode != 0:
        log(err)
        raise RuntimeError("pandoc process exited with non-zero return code.")

    loaded = json.loads(out)
    blocks = loaded['blocks']
    try:
        title = loaded['meta']['title']['c']
    except KeyError:
        raise ValueError("Missing title in meta block in {}".format(filepath))

    return blocks, title
