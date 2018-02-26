r"""Pandoc filter that handles \ifttm commands."""


from enum import Enum
import panflute as pf

from innoconv.utils import parse_cmd


class State(Enum):
    """Enum defining parser states."""
    FIND_IFTTM = 0
    FIND_ELSE_OR_FI = 1
    FIND_FI = 2


class IfttmFilterAction():
    r"""Handle ``\ifttm … \else \fi`` blocks."""

    def __init__(self):
        self._state = State.FIND_IFTTM
        self._element_memory = []

    def filter(self, elem, doc):
        """
        Receive document elements.

        This method parses ``ifttm`` statements.

        :param elem: Element to handle
        :type elem: :class:`panflute.base.Element`
        :param doc: Document
        :type doc: :class:`panflute.elements.Doc`
        """

        if elem is None:
            raise ValueError('elem must not be None!')
        if doc is None:
            raise ValueError('doc must not be None!')

        if not isinstance(elem, (pf.RawBlock, pf.RawInline)):
            if self._state == State.FIND_ELSE_OR_FI:
                # record everything between \if and \else,\fi
                self._element_memory.append(elem)
                return []
            elif self._state == State.FIND_FI:
                # discard everything between \else and \fi
                return []
            return None

        cmd_name = parse_cmd(elem.text)[0]
        ret = None  # None = element unchanged

        # 1) Handle \ifttm

        if self._state == State.FIND_IFTTM and cmd_name == 'ifttm':
            self._state = State.FIND_ELSE_OR_FI
            ret = []

        # 2) Handle \else or \fi

        elif self._state == State.FIND_ELSE_OR_FI:
            if cmd_name == 'else':
                self._state = State.FIND_FI
                ret = []
            elif cmd_name == 'fi':
                ret = self._finalize(elem)

        # 3) Handle \fi

        elif self._state == State.FIND_FI:
            ret = []
            if cmd_name == 'fi':
                ret = self._finalize(elem)

        return ret

    def _prepare_element_memory(self, elem):
        elements = self._element_memory

        # Closing \fi is RawBlock: Pandoc expects block elements. Wrap inline
        # elements.
        if isinstance(elem, pf.Block):
            for i, ret_el in enumerate(elements):
                if not isinstance(ret_el, pf.Block):
                    elements[i] = pf.Para(ret_el)

        return elements

    def _finalize(self, elem):
        ret = self._prepare_element_memory(elem)
        self._element_memory = []
        self._state = State.FIND_IFTTM
        return ret
