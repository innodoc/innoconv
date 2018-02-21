"""Convenience functions for creating common elements."""

from slugify import slugify
import panflute as pf
from mintmod_filter.utils import destringify, pandoc_parse


def create_header(title_str, doc, level=0, auto_id=False):
    """Create a header element.

    Because headers need to be referenced by other elements, references to the
    found headers are stored in the doc properties.
    """
    title = destringify(title_str)
    header = pf.Header(*title, level=level)
    if auto_id:
        header.identifier = slugify(title_str)
    doc.last_header_elem = header
    return header


def create_content_box(title, div_classes, elem_content, doc, level=4,
                       auto_id=False):
    """Create a content box.

    Convenience function for creating content boxes that only differ
    by having diffent titles and classes.
    """
    header = create_header(title, doc, level=level, auto_id=auto_id)
    div = pf.Div(classes=div_classes)
    content = pandoc_parse(elem_content)
    div.content.extend([header] + content)
    return div
