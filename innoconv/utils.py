"""Utility module"""

import sys

from innoconv.constants import ENCODING


def log(msg_string):
    """Log message to stderr.

    :param msg_string: Message that is logged
    :type msg_string: str
    """
    msg_string = "{}\n".format(msg_string)
    if hasattr(sys.stderr, 'buffer'):
        outgoing_bytes = msg_string.encode(ENCODING)
        sys.stderr.buffer.write(outgoing_bytes)
    else:
        sys.stderr.write(msg_string)
    sys.stderr.flush()
