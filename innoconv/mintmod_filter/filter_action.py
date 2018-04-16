"""Pandoc filter that transforms mintmod commands."""

from os import environ
import panflute as pf
from slugify import slugify

from innoconv.errors import ParseError
from innoconv.constants import (REGEX_PATTERNS, ELEMENT_CLASSES,
                                EXERCISE_CMDS_ENVS)
from innoconv.utils import log, destringify, parse_cmd, parse_nested_args
from innoconv.mintmod_filter.environments import Environments
from innoconv.mintmod_filter.commands import Commands
from innoconv.mintmod_filter.math import handle_math


class MintmodFilterAction:

    """The Pandoc filter is defined in this class."""

    def __init__(self, debug=False):
        self._debug = debug
        self._commands = Commands()
        self._environments = Environments()

    def filter(self, elem, doc):
        """
        Receive document elements.

        This method receives document elements from Pandoc and delegates
        handling of simple subtitutions, mintmod commands and
        .ments.

        :param elem: Element to handle
        :type elem: :class:`panflute.base.Element`
        :param doc: Document
        :type doc: :class:`panflute.elements.Doc`
        """

        if elem is None:
            raise ValueError('elem must not be None!')
        if doc is None:
            raise ValueError('doc must not be None!')

        # simple command subtitutions in Math environments
        if isinstance(elem, pf.Math):
            return handle_math(elem)

        elif hasattr(elem, 'format') and elem.format == 'latex':
            # block commands and environments
            if isinstance(elem, pf.RawBlock):
                cmd_name, cmd_args = parse_cmd(elem.text)
                try:
                    if cmd_name == 'begin':
                        return self._handle_environment(elem)
                    return self._handle_command(cmd_name, cmd_args, elem)
                except TypeError as err:
                    self._handle_typeerror(err, cmd_name, cmd_args, elem)

            # inline commands (no inline environments!)
            elif isinstance(elem, pf.RawInline):
                cmd_name, cmd_args = parse_cmd(elem.text)
                try:
                    return self._handle_command(cmd_name, cmd_args, elem)
                except TypeError as err:
                    self._handle_typeerror(err, cmd_name, cmd_args, elem)

        return None  # element unchanged

    def _handle_command(self, cmd_name, cmd_args, elem):
        """Parse and handle mintmod commands."""
        function_name = 'handle_%s' % slugify(cmd_name)
        func = getattr(self._commands, function_name, None)
        if callable(func):
            return func(cmd_args, elem)

        if (not bool(environ.get('INNOCONV_IGNORE_EXERCISES', False)) or
                cmd_name not in EXERCISE_CMDS_ENVS):
            log("Could not handle command %s." % cmd_name, level='WARNING')
        if self._debug:
            return self._unknown_command_debug(cmd_name, elem)
        return None

    @staticmethod
    def _unknown_command_debug(cmd_name, elem):
        """Handle unknown latex commands.

        Output visual feedback about the unknown command.
        """
        classes = ELEMENT_CLASSES['DEBUG_UNKNOWN_CMD'] + [slugify(cmd_name)]
        msg_prefix = pf.Strong(*destringify('Unhandled command:'))
        if isinstance(elem, pf.Block):
            div = pf.Div(classes=classes)
            div.content.extend([pf.Para(msg_prefix), pf.CodeBlock(elem.text)])
            return div
        # RawInline
        span = pf.Span(classes=classes)
        span.content.extend([msg_prefix, pf.Space(), pf.Code(elem.text)])
        return span

    def _handle_environment(self, elem):
        """Parse and handle mintmod environments."""
        match = REGEX_PATTERNS['ENV'].search(elem.text)
        if match is None:
            raise ParseError(
                'Could not parse LaTeX environment: %s...' % elem.text[:50])

        env_name = match.group('env_name')
        inner_code = match.groups()[1]

        # Parse optional arguments
        env_args, rest = parse_nested_args(inner_code)

        function_name = 'handle_%s' % slugify(env_name)
        func = getattr(self._environments, function_name, None)
        if callable(func):
            return func(rest, env_args, elem)

        if (not bool(environ.get('INNOCONV_IGNORE_EXERCISES', False)) or
                env_name not in EXERCISE_CMDS_ENVS):
            log("Could not handle environment %s." % env_name, level='WARNING')

        if self._debug:
            return self._unknown_environment_debug(env_name, elem)
        return None

    @staticmethod
    def _unknown_environment_debug(env_name, elem):
        """Handle unknown latex environment.

        Output visual feedback about the unknown environment.
        """
        classes = ELEMENT_CLASSES['DEBUG_UNKNOWN_ENV'] + [slugify(env_name)]
        div = pf.Div(classes=classes)
        div.content.extend([
            pf.Para(pf.Strong(*destringify('Unhandled environment:'))),
            pf.CodeBlock(elem.text),
        ])
        return div

    @staticmethod
    def _handle_typeerror(err, name, args, elem):
        log('TypeError at command name={} args={} elem={}: {}'.format(
            name, args, elem.__class__.__name__, err))
        import traceback
        traceback.print_tb(err.__traceback__)
