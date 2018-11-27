"""Utility module"""

import json
from subprocess import Popen, PIPE
import sys

from innoconv.constants import ENCODING


class Logger():
    """Logs message to stderr"""

    @classmethod
    def get_logger(cls):
        """Gets the current Logger"""
        try:
            return cls.logger
        except AttributeError:
            cls.logger = Logger()
            return cls.logger

    def __init__(self):
        self.debug = True

    def log(self, msg_string, args):
        """Log message to stderr.

        :param msg_string: Message that is logged
        :type msg_string: str
        """

        if self.debug:
            sys.stderr.write("{}\n".format(msg_string))
            for arg in args:
                sys.stderr.write("{}\n".format(arg))
            sys.stderr.flush()


def set_debug(value=True):
    """Enables debugging
    """
    Logger.get_logger().debug = value


def log(msg_string, *args):
    """Log message to stderr.

    :param msg_string: Message that is logged
    :type msg_string: str
    """
    Logger.get_logger().log(msg_string, args)


def to_ast(filepath):
    """Convert a file to abstract syntax tree using pandoc.

    :param filepath: Path of file
    :type filepath: str

    :rtype: (list of dicts, str)
    :returns: (Pandoc AST, title)

    :raises RuntimeError: if pandoc exits with an error
    :raises ValueError: if no title was found
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
