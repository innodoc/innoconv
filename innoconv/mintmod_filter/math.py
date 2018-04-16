"""Handle mintmod math commands."""

import re
from innoconv.constants import (REGEX_PATTERNS, COMMANDS_IRREGULAR,
                                MATH_SUBSTITUTIONS)
from innoconv.utils import parse_nested_args, log


def handle_math(elem):
    """Handle mintmod text substitutions and some commands with irregular
    arguments."""
    for repl in MATH_SUBSTITUTIONS:
        elem.text = re.sub(repl[0], repl[1], elem.text)

    if REGEX_PATTERNS['IRREG_MATH_CMDS'].search(elem.text):
        def _handle_irregular(cmd_name, cmd_args):
            sub = COMMANDS_IRREGULAR[cmd_name]
            if isinstance(sub, dict):
                try:
                    sub = sub[len(cmd_args)]
                except KeyError:
                    log('Could not find substitution for this number of args: '
                        '{} ({})'.format(cmd_name, cmd_args))
                    raise
            try:
                return sub.format(*cmd_args)
            except IndexError:
                log('Received wrong number of arguments for math command: '
                    '{} ({})'.format(cmd_name, cmd_args))
                raise

        # commands with arguments that may contain nested arguments (can't be
        # handled by regex)
        text = ''
        rest = elem.text
        while rest:
            match = REGEX_PATTERNS['IRREG_MATH_CMDS'].search(rest)
            if match:
                cmd_name = match.group()
                start = match.start()
                text += rest[:start]
                args_til_end = rest[start + len(cmd_name):]
                cmd_args, rest = parse_nested_args(args_til_end)
                text += _handle_irregular(cmd_name[1:], cmd_args)
            else:
                text += rest
                rest = None
        elem.text = text

    return elem
