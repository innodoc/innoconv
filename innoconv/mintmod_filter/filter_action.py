"""The actual Pandoc filter."""

import re
import panflute as pf
from slugify import slugify

from innoconv.errors import ParseError
from innoconv.constants import REGEX_PATTERNS, ELEMENT_CLASSES, COLORS
from innoconv.utils import debug, destringify
from innoconv.mintmod_filter.environments import Environments
from innoconv.mintmod_filter.commands import Commands
from innoconv.mintmod_filter.substitutions import handle_math_substitutions


class FilterAction:

    """The Pandoc filter is defined in this class."""

    def __init__(self):
        self._commands = Commands()
        self._environments = Environments()

    def filter(self, elem, doc):
        """
        Receive document elements.

        This function receives document elements from Pandoc and delegates
        handling of simple subtitutions, mintmod commands and
        environments.

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
            return handle_math_substitutions(elem)

        # block commands and environments
        elif isinstance(elem, pf.RawBlock) and elem.format == 'latex':
            match = REGEX_PATTERNS['CMD'].match(elem.text)
            if match:
                cmd_name = match.groups()[0]
                if cmd_name.startswith('begin'):
                    return self._handle_environment(elem)
                args = re.findall(REGEX_PATTERNS['CMD_ARGS'], elem.text)
                return self._handle_command(cmd_name, args, elem)
            else:
                raise ParseError(
                    'Could not parse LaTeX command: %s...' % elem.text)

        # inline commands
        elif isinstance(elem, pf.RawInline) and elem.format == 'latex':
            # no inline environments are allowed
            match = REGEX_PATTERNS['CMD'].match(elem.text)
            if match:
                cmd_name = match.groups()[0]
                args = re.findall(REGEX_PATTERNS['CMD_ARGS'], elem.text)
                return self._handle_command(cmd_name, args, elem)

        return None  # element unchanged

    def _handle_command(self, cmd_name, args, elem):
        """Parse and handle mintmod commands."""
        function_name = 'handle_%s' % slugify(cmd_name)
        func = getattr(self._commands, function_name, None)
        if callable(func):
            return func(args, elem)
        return self._handle_unknown_command(cmd_name, elem)

    @staticmethod
    def _handle_unknown_command(cmd_name, elem):
        """Handle unknown latex commands.

        Output visual feedback about the unknown command.
        """
        debug("Could not handle command %s." % cmd_name)
        classes = ELEMENT_CLASSES['UNKNOWN_CMD'] + [slugify(cmd_name)]
        attrs = {'style': 'background: %s;' % COLORS['UNKNOWN_CMD']}

        msg = [
            pf.Strong(*destringify('Unhandled command:')),
            pf.Space(), pf.Code(elem.text),
        ]
        if isinstance(elem, pf.Block):
            div = pf.Div(classes=classes, attributes=attrs)
            div.content.extend([pf.Para(*msg)])
            return div
        elif isinstance(elem, pf.Inline):
            span = pf.Span(classes=classes, attributes=attrs)
            span.content.extend(msg)
            return span
        return None

    def _handle_environment(self, elem):
        """Parse and handle mintmod environments."""
        match = REGEX_PATTERNS['ENV'].search(elem.text)
        if match is None:
            raise ParseError(
                'Could not parse LaTeX environment: %s...' % elem.text[:50])

        env_name = match.group('env_name')
        inner_code = match.groups()[1]

        # Parse optional arguments
        env_args = []
        rest = inner_code
        while True:
            match = REGEX_PATTERNS['ENV_ARGS'].search(rest)
            if match is None:
                break
            env_args.append(match.group('arg'))
            rest = match.group('rest')

        function_name = 'handle_%s' % slugify(env_name)
        func = getattr(self._environments, function_name, None)
        if callable(func):
            return func(rest, env_args, elem)
        return self._handle_unknown_environment(env_name, elem)

    @staticmethod
    def _handle_unknown_environment(env_name, elem):
        """Handle unknown latex environment.

        Output visual feedback about the unknown environment.
        """
        debug("Could not handle environment %s." % env_name)
        classes = ELEMENT_CLASSES['UNKNOWN_ENV'] + [slugify(env_name)]
        attrs = {'style': 'background: %s;' % COLORS['UNKNOWN_ENV']}
        div = pf.Div(classes=classes, attributes=attrs)
        msg = pf.Para(pf.Strong(*destringify('Unhandled environment:')),
                      pf.LineBreak(), pf.Code(elem.text))
        div.content.extend([msg])
        return div
