r"""Pandoc filter that handles ``\ifttm`` commands."""


from enum import Enum
import panflute as pf

from innoconv.utils import parse_cmd


class State(Enum):
    """Enum defining parser states."""
    FIND_IFTTM = 0
    FIND_ELSE_OR_FI = 1
    FIND_FI = 2


class IfttmFilterAction():
    r"""Handle conditional code blocks (``\ifttm``)."""

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

    @staticmethod
    def _clean(elem_list, current_elem):
        if not elem_list:
            return elem_list
        ret = []

        # remove empty paragraphs
        for elem in elem_list:
            if not (isinstance(elem, pf.Para) and not elem.content):
                ret.append(elem)

        # if block is expected wrap inlines in para
        if isinstance(current_elem, pf.RawBlock):
            if isinstance(elem_list[0], pf.Inline):
                ret = [pf.Para(*ret)]
        # if inline is expected unwrap Para
        else:
            if isinstance(elem_list[0], pf.Para) and len(elem_list) == 1:
                ret = [el for el in elem_list[0].content]

        return ret

    def _finalize(self, elem):
        self._state = State.FIND_IFTTM
        ret = self._element_memory
        self._element_memory = []
        ret = self._clean(ret, elem)
        return ret
