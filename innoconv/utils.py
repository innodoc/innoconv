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
        self.debug = False

    def set_debug(self, value):
        """Enables debugging"""

        self.debug = value

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
    Logger.get_logger().set_debug(value)


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

    return loaded


def write_json_file(filepath, data, msg):
    """ Writes JSON to file
    """
    with open(filepath, 'w') as out_file:
        json.dump(data, out_file)
    log(msg)
