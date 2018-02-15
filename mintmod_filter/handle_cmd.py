import panflute as pf
from slugify import slugify
from mintmod_filter.utils import debug


def handle_command(cmd, args, elem, doc):
    """Parse and handle mintmod commands"""

    function_name = "handle_cmd_%s" % slugify(cmd)

    if function_name in globals():
        return globals()[function_name](args, elem, doc)

    debug("Could not handle command %s." % cmd)
    return None


def handle_cmd_msection(args, elem, doc):
    """Remember MSection name for later."""
    doc.msection_content = args[0]
    doc.msection_id = slugify(args[0])
    return []


def handle_cmd_special(args, elem, doc):
    """
    Handle latex \special{} commands that often occur with inline html code in
    modules
    """
    if "html:" in args[0]:
        html_code = args[0].replace("html:", "")
        return pf.RawBlock(html_code)
    else:
        return None
