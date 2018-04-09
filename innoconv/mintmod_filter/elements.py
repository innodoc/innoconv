"""Convenience functions for creating common elements."""

from textwrap import shorten
import panflute as pf
from innoconv.constants import ELEMENT_CLASSES
from innoconv.utils import (destringify, parse_fragment, extract_identifier,
                            remember_element)


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

    # Check if environment had an \MLabel identifier
    content, identifier = extract_identifier(content)
    if identifier:
        div.identifier = identifier

    div.content.extend(content)
    return div


def create_header(title_str, doc, level=0):
    """
    Create a header element.

    Because headers need to be referenced by later elements, references to the
    last found header is remembered.
    """
    if not isinstance(doc, pf.Doc):
        raise ValueError('create_header without Doc element')

    title = destringify(title_str)
    header = pf.Header(*title, level=level)
    remember_element(doc, header)
    return header


def create_image(filename, descr, elem, add_descr=True, block=True):
    """Create an image element."""

    img = pf.Image(url=filename, classes=ELEMENT_CLASSES['IMAGE'])

    if add_descr:
        descr = parse_fragment(descr, as_doc=True)
        img.title = shorten(
            pf.stringify(descr).strip(), width=125, placeholder="...")
    else:
        img.title = descr

    if block:
        ret = pf.Div(pf.Plain(img), classes=ELEMENT_CLASSES['FIGURE'])
        remember_element(elem.doc, ret)
        if add_descr:
            ret.content.append(descr.content[0])
    else:
        remember_element(elem.doc, img)
        ret = img

    return ret
