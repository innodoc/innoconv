"""Utility module."""

import json
from subprocess import Popen, PIPE

from innoconv.constants import ENCODING


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
        msg = ("pandoc process returned exit code ({})."
               "This is the pandoc output:\n{}")
        raise RuntimeError(msg.format(proc.returncode, err))

    loaded = json.loads(out)
    blocks = loaded['blocks']
    try:
        title_ast = loaded['meta']['title']['c']
    except KeyError:
        raise ValueError("Missing title in meta block in {}".format(filepath))
    title = ''
    for element in title_ast:
        if element['t'] == 'Str':
            title += element['c']
        elif element['t'] == 'Space':
            title += ' '

    return blocks, title


def walk_ast(ast, func_element, func_array):
    """Walks through an ast

    :param ast: The ast to walk throuhg
    :param func_element: callback for each element
    :param func_array: callback for each array
    """
    def process_ast_element(ast_element, parent_element=None):
        if isinstance(ast_element, list):
            process_ast_array(ast_element, parent_element)
            return
        try:
            try:
                ast_type = ast_element['t']
            except (TypeError, KeyError):
                ast_type = None
            func_element(ast_element, ast_type, parent_element)

            for key in ast_element:
                process_ast_element(ast_element[key],
                                    parent_element=ast_element)
        except (TypeError, KeyError):
            pass

    def process_ast_array(ast_array, parent_element=None):
        func_array(ast_array, parent_element)
        for ast_element in ast_array:
            process_ast_element(ast_element, parent_element)

    if isinstance(ast, list):
        process_ast_array(ast)
    else:
        process_ast_element(ast)
