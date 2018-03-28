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
from innoconv.constants import ELEMENT_CLASSES
from innoconv.utils import log, destringify, parse_fragment
from innoconv.mintmod_filter.elements import create_header


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
        r"""Remember ``\MSection`` name for later.

        ``\MSectionStart`` environment will use this information later.
        """
        create_header(cmd_args[0], level=2, doc=elem.doc, auto_id=True)
        return []

    def handle_msubsection(self, cmd_args, elem):
        r"""Handle ``\MSubsection``"""
        return create_header(cmd_args[0], level=3, doc=elem.doc, auto_id=True)

    def handle_mtitle(self, cmd_args, elem):
        r"""Handle ``\MTitle`` command.

        These is an equivalent to ``\subsubsection``
        """
        return create_header(cmd_args[0], level=4, doc=elem.doc, auto_id=True)

    ###########################################################################
    # Metadata

    def handle_msubject(self, cmd_args, elem):
        r"""Handle ``\MSubject{title}`` command.

        Command defines the document title.
        """
        # self.doc.metadata['title'] = pf.MetaString(cmd_args[0])
        elem.doc.metadata['title'] = pf.MetaString(cmd_args[0])
        return []

    ###########################################################################
    # Links/labels

    def handle_mlabel(self, cmd_args, elem):
        r"""Handle ``\MLabel`` command.

        Will search for the previous header element and update its ID to the
        ID defined in the ``\MLabel`` command."""
        last_header_elem = getattr(elem.doc, "last_header_elem", None)

        if last_header_elem is None:
            log('last_header_elem undefined in '
                'handle_mlabel with cmd_args: %s' % cmd_args,
                level='WARNING')
        else:
            last_header_elem.identifier = cmd_args[0]

        return []

    def handle_msref(self, cmd_args, elem):
        r"""Handle ``\MSRef`` command.

        This command inserts an fragment-style link.
        """
        url = '#%s' % cmd_args[0]
        description = destringify(cmd_args[1])
        return pf.Link(*description, url=url)

    def handle_mnref(self, cmd_args, elem):
        r"""Handle ``\MNRef`` command.

        This command inserts a section link.
        """
        identifier = cmd_args[0]
        span = pf.Span()
        span.attributes = {'data-link-section': identifier}
        span.content = [pf.Str(identifier)]
        return span

    def handle_mextlink(self, cmd_args, elem):
        r"""Handle ``\MExtLink`` command.

        This command inserts an external link.
        """
        url = cmd_args[0]
        text = destringify(cmd_args[1])
        return pf.Link(*text, url=url)

    ###########################################################################
    # Glossary/index

    def handle_mentry(self, cmd_args, elem):
        r"""Handle ``\MEntry`` command.

        This command creates an entry for the glossary/index.
        """
        text = cmd_args[0]
        concept = cmd_args[1]
        strong = pf.Strong()
        strong.content.extend(destringify(text))
        span = pf.Span()
        span.identifier = 'index-{}'.format(slugify(concept))
        span.attributes = {'data-index-concept': concept}
        span.content = [strong]
        return span

    def handle_mindex(self, cmd_args, elem):
        r"""Handle ``\MIndex`` command.

        This command creates an invisible entry for the glossary/index.
        """
        concept = cmd_args[0]
        span = pf.Span()
        span.identifier = 'index-{}'.format(slugify(concept))
        span.attributes = {
            'data-index-concept': concept,
            'hidden': 'hidden',
        }
        return span

    ###########################################################################
    # Media

    def handle_mugraphics(self, cmd_args, elem):
        r"""Handle ``\MUGraphics``.

        Embed an image with title.
        """
        filename = cmd_args[0]
        title = cmd_args[2]
        img = pf.Image(url=filename, title=title)
        # inline
        if isinstance(elem, pf.RawInline):
            return img
        # block
        div = pf.Div(classes=ELEMENT_CLASSES['IMAGE'])
        div.content.extend([pf.Plain(img)])
        return div

    def handle_mugraphicssolo(self, cmd_args, elem):
        r"""Handle ``\MUGraphicsSolo``.

        Embed an image without title.
        """
        filename = cmd_args[0]
        img = pf.Image(url=filename)
        # inline
        if isinstance(elem, pf.RawInline):
            return img
        # block
        div = pf.Div(classes=ELEMENT_CLASSES['IMAGE'])
        div.content.extend([pf.Plain(img)])
        return div

    def handle_myoutubevideo(self, cmd_args, elem):
        r"""Handle ``\MYoutubeVideo``.

        Just return a Link Element
        """
        title, width, height, url = cmd_args
        attrs = {'width': width, 'height': height}
        return pf.Link(
            *destringify(title),
            url=url,
            title=title,
            classes=ELEMENT_CLASSES['MYOUTUBE_VIDEO'],
            attributes=attrs
        )

    ###########################################################################
    # Misc elements

    def handle_special(self, cmd_args, elem):
        r"""Handle ``\special`` command.

        This command is used to embed HTML in LaTeX source.
        """
        if cmd_args[0].startswith('html:'):
            return pf.RawBlock(cmd_args[0][5:], format='html')
        return None

    def handle_mssectionlabelprefix(self, cmd_args, elem):
        r"""Handle ``\MSsectionlabelprefix`` command.

        This command inserts the translation for 'section'.
        """
        return pf.Str('Abschnitt')  # TODO: i18n (#4)

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

    @staticmethod
    def _noop():
        """Return no elements."""
        return []
