"""The actual filter function."""

import re
import panflute as pf
from slugify import slugify

from mintmod_filter.utils import debug, ParseError
from mintmod_filter.handle_env import Environments
from mintmod_filter.handle_cmd import Commands
from mintmod_filter.handle_math_substitutions import handle_math_substitutions

PATTERN_LATEX_CMD = re.compile(r'\\(.*?){', re.DOTALL)
PATTERN_CMD_ARGS = re.compile(r'{(.*?)}')
PATTERN_ENV = re.compile(
    r'\A\\begin{(?P<env_name>[^}]+)}(.+)\\end{(?P=env_name)}\Z', re.DOTALL)
PATTERN_ENV_ARGS = re.compile(
    r'\A{(?P<arg>[^\n\r}]+)}(?P<rest>.+)\Z', re.DOTALL)

COLOR_UNKNOWN = '#FFA500'


class FilterAction:
    def __init__(self):
        self._commands = Commands()
        self._environments = Environments()

    def filter(self, elem, doc):
        """
        Receive document elements.

        This function receives document elements from Pandoc and handles
        delegats handling of simple subtitions, mintmod commands and
        environments.
        """
        if isinstance(elem, pf.Math):
            return handle_math_substitutions(elem, doc)
        elif isinstance(elem, pf.RawBlock) and elem.format == 'latex':
            latex_args = []
            match = PATTERN_LATEX_CMD.match(elem.text)
            if match:
                latex_cmd = match.groups()[0]
                latex_args = re.findall(PATTERN_CMD_ARGS, elem.text)
                if latex_cmd.startswith('begin'):
                    return self._handle_environment(elem, doc)
                else:
                    return self._handle_command(
                        latex_cmd, latex_args, elem, doc)
            else:
                debug('Unhandled RawBlock: %s' % elem.text)
        return None

    def _handle_command(self, cmd, args, elem, doc):
        """Parse and handle mintmod commands."""
        function_name = 'handle_%s' % slugify(cmd)
        func = getattr(self._commands, function_name, None)
        if callable(func):
            return func(args, elem, doc)
        return self._handle_unknown_command(cmd, args, elem, doc)

    def _handle_unknown_command(self, cmd, args, elem, doc):
        """Handle unknown latex commands.

        Will output raw HTML that gives visual feedback about the unknown
        command.
        """
        debug("Could not handle command %s." % cmd)
        wrap = '<div class="unknown-command %s" style="background: %s;"> \
            Unhandled command: <code>%s</code></div>' % \
            (cmd, COLOR_UNKNOWN, elem.text)
        unknown_elem = pf.RawBlock(wrap, format="html")
        return unknown_elem

    def _handle_environment(self, elem, doc):
        """Parse and handle mintmod environments."""
        match = PATTERN_ENV.search(elem.text)
        if match is None:
            raise ParseError(
                'Could not parse environment: %s...' % elem.text[:50])

        env_name = match.group('env_name')
        inner_code = match.groups()[1]

        # Parse optional arguments
        env_args = []
        rest = inner_code
        while True:
            match = PATTERN_ENV_ARGS.search(rest)
            if match is None:
                break
            env_args.append(match.group('arg'))
            rest = match.group('rest')

        function_name = 'handle_%s' % slugify(env_name)
        func = getattr(self._environments, function_name, None)
        if callable(func):
            return func(rest, env_args, doc)
        return self._handle_unknown_environment(env_name, env_args, rest, doc)

    def _handle_unknown_environment(self, env_name, args, elem_content, doc):
        """Handle unknown latex environment.

        Will output raw HTML that gives visual feedback about the unknown
        environment.
        """
        debug("Could not handle environment %s." % env_name)
        wrap = '<div class="unknown-environment %s" style="background: %s;"> \
            Unhandled environment: <code>%s</code></div>' % \
            (env_name, COLOR_UNKNOWN, elem_content)
        unknown_elem = pf.RawBlock(wrap, format="html")
        return unknown_elem
