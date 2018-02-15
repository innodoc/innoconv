"""The actual filter function."""

import re
import panflute as pf

from mintmod_filter.utils import debug
from mintmod_filter.handle_env import handle_environment
from mintmod_filter.handle_cmd import handle_command
from mintmod_filter.handle_math_substitutions import handle_math_substitutions

PATTERN_LATEX_CMD = re.compile(r'\\(.*?){', re.DOTALL)
PATTERN_CMD_ARGS = re.compile(r'{(.*?)}')
PATTERN_SPECIAL = re.compile(r'\\special{html:(.*)}')
PATTERN_MSECTION = re.compile(r'\\MSection{([^}]*)}')
PATTERN_ENV_ARGS = re.compile(
    r'\A{(?P<arg>[^\n\r}]+)}(?P<rest>.+)\Z', re.DOTALL)


def filter_action(elem, doc):
    """Walk document AST."""
    if isinstance(elem, pf.Math):
        return handle_math_substitutions(elem, doc)
    elif isinstance(elem, pf.RawBlock) and elem.format == 'latex':
        latex_args = []
        match = PATTERN_LATEX_CMD.match(elem.text)
        if match:
            latex_cmd = match.groups()[0]
            latex_args = re.findall(PATTERN_CMD_ARGS, elem.text)
            if latex_cmd.startswith('begin'):
                return handle_environment(elem, doc)
            else:
                return handle_command(latex_cmd, latex_args, elem, doc)
                debug("unhandled command", latex_cmd)
                debug("with args", latex_args)

        else:
            debug('Unhandled RawBlock: %s' % elem.text)
    return None
