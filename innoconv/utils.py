"""Utility module."""

import asyncio
import logging
import json
from subprocess import PIPE, Popen

from innoconv.constants import ENCODING


def to_string(ast):
    """
    Convert AST to string (handles String and Space only).

    :param ast: Content AST.
    :type ast: List
    """
    out = ""
    for element in ast:
        if element["t"] == "Str":
            out += element["c"]
        elif element["t"] == "Space":
            out += " "
    return out


async def to_ast(filepath, ignore_missing_title=False):
    """
    Convert a file to abstract syntax tree using pandoc.

    :param filepath: Path of file
    :type filepath: str

    :param ignore_missing_title: Accept missing title in source file
    :type ignore_missing_title: bool

    :rtype: (list of dicts, str)
    :returns: (Pandoc AST, title)

    :raises RuntimeError: if pandoc exits with an error
    :raises ValueError: if no title was found
    """
    pandoc_cmd = ["pandoc", "--to=json", filepath]
    proc = await asyncio.create_subprocess_exec(*pandoc_cmd, stdout=PIPE, stderr=PIPE)
    try:
        out, err = await asyncio.wait_for(proc.communicate(), 60)
    except asyncio.TimeoutError:
        logging.error('Pandoc process timed out: %s', pandoc_cmd.join(' '))

    if proc.returncode != 0:
        msg = "Pandoc process returned exit code ({}). Pandoc output:\n{}"
        raise RuntimeError(msg.format(proc.returncode, err.decode(ENCODING)))

    loaded = json.loads(out.decode(ENCODING))
    blocks = loaded["blocks"]
    try:
        title_ast = loaded["meta"]["title"]["c"]
    except KeyError:
        if ignore_missing_title:
            title_ast = []
        else:
            raise ValueError("Missing title in meta block in {}".format(filepath))
    title = to_string(title_ast)
    try:
        short_title_ast = loaded["meta"]["short_title"]["c"]
    except KeyError:
        short_title_ast = None
    short_title = to_string(short_title_ast) if short_title_ast else title

    return blocks, title, short_title
