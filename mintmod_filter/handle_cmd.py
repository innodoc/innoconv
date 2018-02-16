r"""Handle mintmod LaTex commands.

Convention: Provide a `handle_CMDNAME` function for handling `\CMDNAME`
            command. You need to slugify the name.

Example: `handle_msection` method will receive the `MSection` command.
"""

import panflute as pf
from slugify import slugify
from mintmod_filter.utils import debug


def handle_command(cmd, args, elem, doc):
    """Parse and handle mintmod commands."""
    function_name = "handle_%s" % slugify(cmd)

    if function_name in globals():
        return globals()[function_name](args, elem, doc)

    debug("Could not handle command %s." % cmd)
    return None


def handle_msection(args, elem, doc):
    """Remember `MSection` name for later.

    `MSectionStart` environment will use this information later.
    """
    doc.msection_content = args[0]
    doc.msection_id = slugify(args[0])
    return []

def handle_cmd_mtitle(args, elem, doc):
    """
    handle \MTitle{} commands that are used as further equivalents to
    \subsubsection{}
    """
    header = pf.Header(pf.RawInline(args[0]), level=4)  # TODO i18n?
    return header

def handle_special(args, elem, doc):
    r"""Handle `special` command.

    This command is used to embed HTML in LaTeX source.
    """
    if "html:" in args[0]:
        html_code = args[0].replace("html:", "")
        return pf.RawBlock(html_code)
    else:
        return None
