"""Utility module."""

import json
from subprocess import PIPE, Popen

from innoconv.constants import ENCODING


def to_ast(filepath):
    """
    Convert a file to abstract syntax tree using pandoc.

    :param filepath: Path of file
    :type filepath: str

    :rtype: (list of dicts, str)
    :returns: (Pandoc AST, title)

    :raises RuntimeError: if pandoc exits with an error
    :raises ValueError: if no title was found
    """
    pandoc_cmd = ["pandoc", "--to=json", filepath]
    proc = Popen(pandoc_cmd, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate(timeout=60)
    out = out.decode(ENCODING)
    err = err.decode(ENCODING)

    if proc.returncode != 0:
        msg = (
            "pandoc process returned exit code ({})."
            "This is the pandoc output:\n{}"
        )
        raise RuntimeError(msg.format(proc.returncode, err))

    loaded = json.loads(out)
    blocks = loaded["blocks"]
    try:
        title_ast = loaded["meta"]["title"]["c"]
    except KeyError:
        raise ValueError("Missing title in meta block in {}".format(filepath))
    title = ""
    for element in title_ast:
        if element["t"] == "Str":
            title += element["c"]
        elif element["t"] == "Space":
            title += " "

    return blocks, title
