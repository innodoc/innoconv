r"""
Handle mintmod LaTeX commands.

.. note::
    Provide a ``handle_CMDNAME`` function for handling ``CMDNAME`` command.
    You need to `slugify <https://github.com/un33k/python-slugify>`_ the
    command name.

    Example: ``handle_msection`` method will receive the command ``\MSection``.
"""

import panflute as pf
from slugify import slugify
from innoconv.constants import (ELEMENT_CLASSES, MINTMOD_SUBJECTS,
                                REGEX_PATTERNS, INDEX_LABEL_PREFIX)
from innoconv.utils import (block_wrap, destringify, parse_fragment, log,
                            get_remembered_element, to_inline)
from innoconv.mintmod_filter.elements import create_header, create_image


class Commands():

    r"""
    Handlers for commands are defined here.

    Given the command:

    .. code-block:: latex

        \MSection{Foo}

    The handler method ``handle_msection`` receives the following arguments:

    .. hlist::
        :columns: 1

        * ``cmd_args``: ``['Foo']``
        * ``elem``: :class:`panflute.base.Element`
    """

    # pylint: disable=unused-argument,no-self-use,too-many-public-methods

    ###########################################################################
    # Sections

    def handle_msection(self, cmd_args, elem):
        r"""Handle ``\MSection`` command."""
        return create_header(cmd_args[0], level=2, doc=elem.doc)

    def handle_msubsection(self, cmd_args, elem):
        r"""Handle ``\MSubsection``"""
        return create_header(cmd_args[0], level=3, doc=elem.doc)

    def handle_msubsubsection(self, cmd_args, elem):
        r"""Handle ``\MSubsubsection``"""
        return create_header(cmd_args[0], level=4, doc=elem.doc)

    def handle_mtitle(self, cmd_args, elem):
        r"""Handle ``\MTitle`` command.

        This is an equivalent to ``\subsubsection``
        """
        return create_header(cmd_args[0], level=4, doc=elem.doc)

    def handle_msubsubsubsectionx(self, cmd_args, elem):
        r"""Handle ``\MSubsubsubsectionx`` command. Which will generate a level
        5 header."""
        return create_header(cmd_args[0], level=5, doc=elem.doc)

    ###########################################################################
    # Metadata

    def handle_msubject(self, cmd_args, elem):
        r"""Handle ``\MSubject{title}`` command.

        Command defines the document title.
        """
        elem.doc.metadata['title'] = pf.MetaString(cmd_args[0])
        return []

    def handle_msetsubject(self, cmd_args, elem):
        r"""Handle ``\MSetSubject{}`` command.

        Command defines the category.
        """
        elem.doc.metadata['subject'] = pf.MetaString(
            MINTMOD_SUBJECTS[cmd_args[0]])
        return []

    ###########################################################################
    # Links/labels

    def handle_mlabel(self, cmd_args, elem):
        r"""Handle ``\MLabel`` command.

        Will search for the previous header element and update its ID to the
        ID defined in the ``\MLabel`` command.

        The command can occur in an environment that is parsed by a
        subprocess. In this case there's no last header element. The process
        can't set the ID because it can't access the doc tree. Instead it
        replaces the ``\MLabel`` by an element that is found by the parent
        process using function :py:func:`innoconv.utils.extract_identifier`.
        """

        identifier = cmd_args[0]

        # attach identifier to previous element
        try:
            get_remembered_element(elem.doc).identifier = identifier
            return []
        except AttributeError:
            pass

        # otherwise return a div/span with ID that is parsed in the parent
        # process
        if isinstance(elem, pf.Block):
            ret = pf.Div()
        else:
            ret = pf.Span()
        ret.identifier = '{}-{}'.format(INDEX_LABEL_PREFIX, identifier)
        ret.classes = [INDEX_LABEL_PREFIX]
        ret.attributes = {'hidden': 'hidden'}
        return ret

    def handle_mref(self, cmd_args, elem):
        r"""Handle ``\MRef`` command.

        This command translates to ``\vref``.
        """
        url = '#%s' % cmd_args[0]
        # TODO: insert referenced number (e.g. '1.2')
        return block_wrap(pf.Link(pf.Str('PLACEHOLDER'), url=url), elem)

    def handle_msref(self, cmd_args, elem):
        r"""Handle ``\MSRef`` command.

        This command inserts a fragment-style link.
        """
        url = '#%s' % cmd_args[0]
        description = destringify(cmd_args[1])
        return block_wrap(pf.Link(*description, url=url), elem)

    def handle_mnref(self, cmd_args, elem):
        r"""Handle ``\MNRef`` command.

        This command inserts a section link.
        """
        identifier = cmd_args[0]
        span = pf.Span()
        span.attributes = {'data-link-section': identifier}
        span.content = [pf.Str(identifier)]
        return block_wrap(span, elem)

    def handle_mextlink(self, cmd_args, elem):
        r"""Handle ``\MExtLink`` command.

        This command inserts an external link.
        """
        url = cmd_args[0]
        text = destringify(cmd_args[1])
        link = pf.Link(*text, url=url)
        return block_wrap(link, elem)

    ###########################################################################
    # Glossary/index

    def handle_mentry(self, cmd_args, elem):
        r"""Handle ``\MEntry`` command.

        This command creates an entry for the glossary/index.
        """

        if isinstance(elem, pf.Block):
            log("Warning: Expected Inline for MNRef: {}".format(cmd_args))

        text = cmd_args[0]
        concept = cmd_args[1]
        strong = pf.Strong()

        strong.content.extend(parse_fragment(text)[0].content)
        span = pf.Span()
        span.identifier = 'index-{}'.format(slugify(concept))
        span.attributes = {'data-index-concept': concept}
        span.content = [strong]
        return block_wrap(span, elem)

    def handle_mindex(self, cmd_args, elem):
        r"""Handle ``\MIndex`` command.

        This command creates an invisible entry for the glossary/index.
        """

        if isinstance(elem, pf.Block):
            log("Warning: Expected Inline for MNRef: {}".format(cmd_args))

        concept = cmd_args[0]
        span = pf.Span()
        span.identifier = 'index-{}'.format(slugify(concept))
        span.attributes = {
            'data-index-concept': concept,
            'hidden': 'hidden',
        }
        return block_wrap(span, elem)

    ###########################################################################
    # Media

    def handle_mgraphics(self, cmd_args, elem, add_desc=True):
        r"""Handle ``\MGraphics``.

        Embed an image with title.

        Example: \MGraphics{img.png}{scale=1}{title}
        """
        is_block = isinstance(elem, pf.Block)
        return create_image(cmd_args[0], cmd_args[2], elem, block=is_block)

    def handle_mgraphicssolo(self, cmd_args, elem):
        r"""Handle ``\MGraphicsSolo``.

        Embed an image without title. Uses filename as image title.
        """
        is_block = isinstance(elem, pf.Block)
        return create_image(cmd_args[0], cmd_args[0], elem, block=is_block,
                            add_descr=False)

    def handle_mugraphics(self, cmd_args, elem):
        r"""Handle ``\MUGraphics``.

        Embed an image with title.
        """
        return self.handle_mgraphics([cmd_args[0], None, cmd_args[2]], elem)

    def handle_mugraphicssolo(self, cmd_args, elem):
        r"""Handle ``\MUGraphicsSolo``.

        Embed an image without title.
        """
        return self.handle_mgraphicssolo(cmd_args, elem)

    def handle_myoutubevideo(self, cmd_args, elem):
        r"""Handle ``\MYoutubeVideo``.

        Just return a Link Element.
        """
        title, _, _, url = cmd_args
        link = pf.Link(
            *destringify(title),
            url=url,
            title=title,
            classes=ELEMENT_CLASSES['MYOUTUBE_VIDEO']
        )
        return block_wrap(link, elem)

    def handle_mvideo(self, cmd_args, elem):
        r"""Handle ``\MVideo``.

        Just return a Link Element.
        """
        filename = '{}.mp4'.format(cmd_args[0])
        title = cmd_args[1]
        link = pf.Link(
            *destringify(title),
            url=filename,
            title=title,
            classes=ELEMENT_CLASSES['MVIDEO']
        )
        return block_wrap(link, elem)

    def handle_mtikzauto(self, cmd_args, elem):
        r"""Handle ``\MTikzAuto`` command.

        Create a ``CodeBlock`` with TikZ code.
        """
        tikz_code = REGEX_PATTERNS['STRIP_HASH_LINE'].sub('', cmd_args[0])
        if isinstance(elem, pf.Inline):
            ret = pf.Code(tikz_code)
        else:
            ret = pf.CodeBlock(tikz_code)
        ret.classes = ELEMENT_CLASSES['MTIKZAUTO']
        return ret

    ###########################################################################
    # Misc elements

    def handle_special(self, cmd_args, elem):
        r"""Handle ``\special`` command.

        This command is used to embed HTML in LaTeX source.
        """
        if cmd_args[0].startswith('html:'):
            return pf.RawBlock(cmd_args[0][5:], format='html')
        return None

    def handle_minputhint(self, cmd_args, elem):
        r"""Handle ``\MInputHint`` command."""
        content = parse_fragment(cmd_args[0])
        if isinstance(elem, pf.Block):
            div = pf.Div(classes=ELEMENT_CLASSES['MINPUTHINT'])
            div.content.extend(content)
            return div
        span = pf.Span(classes=ELEMENT_CLASSES['MINPUTHINT'])
        if content and isinstance(content[0], pf.Para):
            span.content.extend(content[0].content)
        return span

    def handle_mequationitem(self, cmd_args, elem):
        r"""Handle ``\MEquationItem`` command."""

        if len(cmd_args) != 2:
            raise ValueError(
                r'\MEquationItem needs 2 arguments. Received: {}'.format(
                    cmd_args))

        content_left = parse_fragment(cmd_args[0])
        content_right = parse_fragment(cmd_args[1])

        content = to_inline(
            [
                content_left,
                pf.Math(r'\;\;=\;', format='InlineMath'),
                content_right,
            ]
        )

        if isinstance(elem, pf.Block):
            return pf.Plain(content)
        return content

    ###########################################################################
    # Command pass-thru

    def handle_mzxyzhltrennzeichen(self, cmd_args, elem):
        r"""Handle ``\MZXYZhltrennzeichen`` command.

        It is transformed to a ``\decmarker`` command and later substituted
        by MathJax. This is already in math substitions but as it occurs
        outside of math environments it's defined here too.
        """
        if isinstance(elem, pf.Block):
            raise ValueError(
                r'Encountered \MZXYZhltrennzeichen as block element!')
        return pf.Math(r'\decmarker', format='InlineMath')

    def handle_mzahl(self, cmd_args, elem):
        r"""Handle ``\MZahl`` command.

        This is a math command but in fact occurs also in text.
        """
        if isinstance(elem, pf.Block):
            raise ValueError(
                r'Encountered \MZahl as block element!')
        return pf.Math(r'\num{{{}.{}}}'.format(cmd_args[0], cmd_args[1]),
                       format='InlineMath')

    ###########################################################################
    # Simple substitutions

    def handle_glqq(self, cmd_args, elem):
        r"""Handle ``\glqq`` command."""
        return pf.Str('„')

    def handle_grqq(self, cmd_args, elem):
        r"""Handle ``\grqq`` command."""
        return pf.Str('“')

    def handle_quad(self, cmd_args, elem):
        r"""Handle ``\quad`` command."""
        return pf.Space()

    ###########################################################################
    # Formatting

    def handle_modstextbf(self, cmd_args, elem):
        r"""Handle \modstextbf command."""
        return pf.Strong(*parse_fragment(cmd_args[0])[0].content)

    def handle_modsemph(self, cmd_args, elem):
        r"""Handle \modsemph command."""
        return pf.Emph(*parse_fragment(cmd_args[0])[0].content)

    def handle_highlight(self, cmd_args, elem):
        r"""Handle \highlight command.

        This seems to be some sort of formatting command. There's no
        documentation and it does nothing in the mintmod code. We just keep
        the information here.
        """
        return pf.Span(*parse_fragment(cmd_args[0])[0].content,
                       classes=ELEMENT_CLASSES['HIGHLIGHT'])

    def handle_newline(self, cmd_args, elem):
        r"""Handle \newline command."""
        return pf.LineBreak()

    ###########################################################################
    # No-ops

    def handle_mdeclaresiteuxid(self, cmd_args, elem):
        r"""Handle ``\MDeclareSiteUXID`` command.

        This command is used to embed IDs. This is not relevant anymore and
        becomes a no-op.
        """
        return self._noop()

    def handle_mmodstartbox(self, cmd_args, elem):
        r"""Handle ``\MModStartBox`` command.

        This command displays a table of content for the current chapter. This
        is handled elswhere and becomes a no-op.
        """
        return self._noop()

    def handle_mpragma(self, cmd_args, elem):
        r"""Handle ``\MPragma`` command.

        This command was used to embed build time flags for mintmod. It becomes
        a no-op.
        """
        return self._noop()

    def handle_vspace(self, cmd_args, elem):
        r"""Handle ``\vspace`` command.

        A display related command. It becomes a no-op.
        """
        return self._noop()

    def handle_newpage(self, cmd_args, elem):
        r"""Handle ``\newpage`` command.

        A display related command. It becomes a no-op.
        """
        return self._noop()

    def handle_mprintindex(self, cmd_args, elem):
        r"""Handle ``\MPrintIndex`` command.

        Index will be printed automatically. It becomes a no-op.
        """
        return self._noop()

    def handle_msetsectionid(self, cmd_args, elem):
        r"""Handle ``\MSetSectionID`` command.

        This command is used solely for tikz images. It becomes a no-op.
        """
        return self._noop()

    def handle_mcontenttable(self, cmd_args, elem):
        r"""Handle ``\MContentTable`` command."""
        return self._noop()

    def handle_mglobalstart(self, cmd_args, elem):
        r"""Handle ``\MGlobalStart`` command."""
        return self._noop()

    def handle_mpullsite(self, cmd_args, elem):
        r"""Handle ``\MPullSite`` command."""
        return self._noop()

    def handle_mglobalchaptertag(self, cmd_args, elem):
        r"""Handle ``\MGlobalChapterTag`` command."""
        return self._noop()

    def handle_mglobalconftag(self, cmd_args, elem):
        r"""Handle ``\MGlobalConfTag`` command."""
        return self._noop()

    def handle_mgloballogouttag(self, cmd_args, elem):
        r"""handle ``\MGlobalLogoutTag`` command."""
        return self._noop()

    def handle_mgloballogintag(self, cmd_args, elem):
        r"""Handle ``\MGlobalLoginTag`` command."""
        return self._noop()

    def handle_mgloballocationtag(self, cmd_args, elem):
        r"""Handle ``\MGlobalLocationTag`` command."""
        return self._noop()

    def handle_mglobaldatatag(self, cmd_args, elem):
        r"""Handle ``\MGlobalDataTag`` command."""
        return self._noop()

    def handle_mglobalsearchtag(self, cmd_args, elem):
        r"""Handle ``\MGlobalSearchTag`` command."""
        return self._noop()

    def handle_mglobalfavotag(self, cmd_args, elem):
        r"""Handle ``\MGlobalFavoTag`` command."""
        return self._noop()

    def handle_mglobalstesttag(self, cmd_args, elem):
        r"""Handle ``\MGlobalSTestTag`` command."""
        return self._noop()

    def handle_mwatermarksettings(self, cmd_args, elem):
        r"""Handle ``\MWatermarkSettings`` command."""
        return self._noop()

    def handle_smallskip(self, cmd_args, elem):
        r"""Handle ``\smallskip`` command."""
        return self._noop()

    def handle_medskip(self, cmd_args, elem):
        r"""Handle ``\medskip`` command."""
        return self._noop()

    def handle_bigskip(self, cmd_args, elem):
        r"""Handle ``\bigskip`` command."""
        return self._noop()

    def handle_hspace(self, cmd_args, elem):
        r"""Handle ``\hspace`` and ``\hspace*`` command."""
        return self._noop()

    def handle_clearpage(self, cmd_args, elem):
        r"""Handle ``\clearpage`` command."""
        return self._noop()

    def handle_noindent(self, cmd_args, elem):
        r"""Handle ``\noindent`` command."""
        return self._noop()

    @staticmethod
    def _noop():
        """Return no elements."""
        return []
