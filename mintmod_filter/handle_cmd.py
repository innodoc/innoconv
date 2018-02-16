r"""Handle mintmod LaTex commands.

Convention: Provide a ``handle_CMDNAME`` function for handling ``CMDNAME``
            command. You need to slugify the name.

Example: ``handle_msection`` method will receive the ``MSection`` command.
"""

import panflute as pf
from slugify import slugify


class Commands():
    def handle_msection(self, args, elem, doc):
        """Remember ``MSection`` name for later.

        `MSectionStart` environment will use this information later.
        """
        doc.msection_content = args[0]
        doc.msection_id = slugify(args[0])
        return []

    def handle_cmd_mtitle(self, args, elem, doc):
        """Handle `MTitle`` command.

        These is an equivalent to ``subsubsection``
        """
        header = pf.Header(pf.RawInline(args[0]), level=4)  # TODO i18n?
        return header

    def handle_special(self, args, elem, doc):
        r"""Handle `special` command.

        This command is used to embed HTML in LaTeX source.
        """
        if "html:" in args[0]:
            html_code = args[0].replace("html:", "")
            return pf.RawBlock(html_code)
        else:
            return None
