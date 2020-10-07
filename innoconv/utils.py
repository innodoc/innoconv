"""Utility module."""

import json
from subprocess import PIPE, Popen

from innoconv.constants import ALLOWED_SECTION_TYPES, ENCODING


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


def to_ast(filepath, ignore_missing_title=False):
    """
    Convert a file to abstract syntax tree using pandoc.

    :param filepath: Path of file
    :type filepath: str

    :param ignore_missing_title: Accept missing title in source file
    :type ignore_missing_title: bool

    :rtype: (list of dicts, str, str, str)
    :returns: (Pandoc AST, title, short_title, section_type)

    :raises RuntimeError: if pandoc exits with an error
    :raises ValueError: if no title was found
    """
    pandoc_cmd = ["pandoc", "--strip-comments", "--to=json", filepath]
    proc = Popen(pandoc_cmd, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate(timeout=60)
    out = out.decode(ENCODING)
    err = err.decode(ENCODING)

    if proc.returncode != 0:
        msg = (
            f"pandoc process returned exit code ({proc.returncode}). "
            f"This is the pandoc output:\n{err}"
        )
        raise RuntimeError(msg)

    loaded = json.loads(out)
    blocks = loaded["blocks"]

    # extract title
    try:
        title_ast = loaded["meta"]["title"]["c"]
    except KeyError as err:
        if ignore_missing_title:
            title_ast = []
        else:
            msg = f"Missing title in meta block in {filepath}"
            raise ValueError(msg) from err
    title = to_string(title_ast)
    try:
        short_title_ast = loaded["meta"]["short_title"]["c"]
    except KeyError:
        short_title_ast = None
    short_title = to_string(short_title_ast) if short_title_ast else title

    # extract type
    section_type = None
    try:
        section_type = to_string(loaded["meta"]["type"]["c"])
        if section_type not in ALLOWED_SECTION_TYPES:
            raise ValueError(f"Invalid section type: {section_type}")
    except KeyError:
        pass

    return blocks, title, short_title, section_type
