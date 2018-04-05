"""Convenience functions for creating common elements."""

import panflute as pf
from innoconv.utils import destringify, parse_fragment, extract_identifier


def create_content_box(elem_content, elem_classes):
    """
    Create a content box.

    Convenience function for creating content boxes that only differ
    by having diffent content and classes.
    """
    if not elem_classes or elem_classes == []:
        msg = 'create_content_box without element classes: {}'.format(
            elem_classes)
        raise ValueError(msg)

    if not elem_content or elem_content == '':
        msg = 'create_content_box without element content: {}'.format(
            elem_content)
        raise ValueError(msg)

    div = pf.Div(classes=elem_classes)
    content = parse_fragment(elem_content)

    content, identifier = extract_identifier(content)
    if identifier:
        div.identifier = identifier

    div.content.extend(content)
    return div


def create_header(title_str, doc, level=0):
    """
    Create a header element.

    Because headers need to be referenced by later elements, references to the
    last found header is stored in the doc.
    """
    if not isinstance(doc, pf.Doc):
        raise ValueError('create_title without Doc element')

    title = destringify(title_str)
    header = pf.Header(*title, level=level)
    doc.last_header_elem = header
    return header
