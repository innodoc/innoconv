"""Handle mintmod LaTeX commands."""
import panflute as pf
from mintmod_filter.elements import create_header
from mintmod_filter.utils import debug, destringify


class Commands():

    """Handlers for commands are defined here.

    Convention: Provide a ``handle_CMDNAME`` function for handling ``CMDNAME``
    command. You need to slugify the command name.

    Example: ``handle_msection`` method will receive the ``MSection`` command.
    """

    # pylint: disable=unused-argument,no-self-use

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

    def handle_special(self, args, elem):
        """Handle ``special`` command.

        This command is used to embed HTML in LaTeX source.
        """
        if "html:" in args[0]:
            html_code = args[0].replace("html:", "")
            return pf.RawBlock(html_code)
        return None

    def handle_msubject(self, args, elem):
        """Handle ``MSubject{title}`` command.

        Command defines the document title.
        """
        elem.doc.metadata['title'] = pf.MetaString(args[0])
        return []

    def handle_msref(self, args, elem):
        """Handle ``MSRef`` command.

        This command inserts an fragment-style link.
        """
        url = '#%s' % args[0]
        description = destringify(args[1])
        return pf.Link(*description, url=url)

    def handle_mssectionlabelprefix(self, args, elem):
        """Handle ``MSsectionlabelprefix`` command.

        This command inserts a translation.
        """
        return pf.Str('Abschnitt')  # TODO: i18n

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
