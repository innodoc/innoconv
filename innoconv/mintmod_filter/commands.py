"""Handle mintmod LaTeX commands."""

import panflute as pf
from innoconv.constants import ELEMENT_CLASSES
from innoconv.utils import debug, destringify
from innoconv.mintmod_filter.elements import create_header


class Commands():

    """Handlers for commands are defined here.

    Convention: Provide a ``handle_CMDNAME`` function for handling ``CMDNAME``
    command. You need to slugify the command name.

    Example: ``handle_msection`` method will receive the ``MSection`` command.
    """

    # pylint: disable=unused-argument,no-self-use

    ###########################################################################
    # Sections

    def handle_msection(self, args, elem):
        """Remember ``MSection`` name for later.

        ``MSectionStart`` environment will use this information later.
        """
        create_header(args[0], level=2, doc=elem.doc, auto_id=True)
        return []

    def handle_msubsection(self, args, elem):
        """Handle ``MSubsection``"""
        return create_header(args[0], level=3, doc=elem.doc, auto_id=True)

    def handle_mtitle(self, args, elem):
        """Handle ``MTitle`` command.

        These is an equivalent to ``subsubsection``
        """
        return create_header(args[0], level=4, doc=elem.doc, auto_id=True)

    ###########################################################################
    # Metadata

    def handle_msubject(self, args, elem):
        """Handle ``MSubject{title}`` command.

        Command defines the document title.
        """
        # self.doc.metadata['title'] = pf.MetaString(args[0])
        elem.doc.metadata['title'] = pf.MetaString(args[0])
        return []

    ###########################################################################
    # Links/labels

    def handle_mlabel(self, args, elem):
        """Handle ``MLabel`` command.

        Will search for the previous header element and update its ID to the
        ID defined in the ``MLabel`` command."""
        last_header_elem = getattr(elem.doc, "last_header_elem", None)

        if last_header_elem is None:
            debug("WARNING: last_header_elem undefined in handle_mlabel with"
                  "args: %s" % args)
            return None

        last_header_elem.identifier = args[0]
        return []

    def handle_msref(self, args, elem):
        """Handle ``MSRef`` command.

        This command inserts an fragment-style link.
        """
        url = '#%s' % args[0]
        description = destringify(args[1])
        return pf.Link(*description, url=url)

    def handle_mextlink(self, args, elem):
        """Handle ``MExtLink`` command.

        This command inserts an external link.
        """
        url = args[0]
        text = destringify(args[1])
        return pf.Link(*text, url=url)

    ###########################################################################
    # Graphics

    def handle_mugraphics(self, args, elem):
        """Handle ``MUGraphics``.

        Embed an image with title.
        """
        filename = args[0]
        title = args[2]
        img = pf.Image(url=filename, title=title)
        if isinstance(elem, pf.RawInline):
            return img
        elif isinstance(elem, pf.RawBlock):
            div = pf.Div(classes=ELEMENT_CLASSES['IMAGE'])
            div.content.extend([pf.Plain(img)])
            return div
        return None

    def handle_mugraphicssolo(self, args, elem):
        """Handle ``MUGraphicsSolo``.

        Embed an image without title.
        """
        filename = args[0]
        img = pf.Image(url=filename)
        if isinstance(elem, pf.RawInline):
            return img
        elif isinstance(elem, pf.RawBlock):
            div = pf.Div(classes=ELEMENT_CLASSES['IMAGE'])
            div.content.extend([pf.Plain(img)])
            return div
        return None

    ###########################################################################
    # Misc elements

    def handle_special(self, args, elem):
        """Handle ``special`` command.

        This command is used to embed HTML in LaTeX source.
        """
        if "html:" in args[0]:
            html_code = args[0].replace("html:", "")
            return pf.RawBlock(html_code)
        return None

    def handle_mssectionlabelprefix(self, args, elem):
        """Handle ``MSsectionlabelprefix`` command.

        This command inserts a translation.
        """
        return pf.Str('Abschnitt')  # TODO: i18n

    ###########################################################################
    # Simple substitutions

    def handle_glqq(self, args, elem):
        """Handle ``glqq`` command."""
        return pf.Str('„')

    def handle_grqq(self, args, elem):
        """Handle ``grqq`` command."""
        return pf.Str('“')

    ###########################################################################
    # No-ops

    def handle_mdeclaresiteuxid(self, args, elem):
        """Handle ``MDeclareSiteUXID`` command.

        This command is used to embed IDs. This is not relevant anymore and
        becomes a no-op.
        """
        return self._noop()

    def handle_mmodstartbox(self, args, elem):
        """Handle ``MModStartBox`` command.

        This command displays a table of content for the current chapter. This
        is handled elswhere and becomes a no-op.
        """
        return self._noop()

    def handle_mpragma(self, args, elem):
        """Handle ``MPragma`` command.

        This command was used to embed build time flags for mintmod. It becomes
        a no-op.
        """
        return self._noop()

    @staticmethod
    def _noop():
        """Return no elements."""
        return []
