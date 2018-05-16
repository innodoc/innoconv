"""Convenience functions and classes for creating common elements."""

from textwrap import shorten
import panflute as pf
from innoconv.constants import ELEMENT_CLASSES
from innoconv.utils import (destringify, parse_fragment, extract_identifier,
                            remember_element)


class Exercise(pf.Element):
    """
    Class that inherits from pf.Element and will return pf.Code instances, with
    special classes and attributes, depending on the passed mintmod class.
    """
    __slots__ = ['identifier', 'classes', 'attributes']

    def __new__(cls, *args, **kwargs):
        """ The __new__ function expects a keyword argument with the key
        'mintmod_class' that specifies the type of exercise in the mintmod
        converter.
        """
        mintmod_class = kwargs.get('mintmod_class', None)
        oktypes = kwargs.get('oktypes', None)
        cmd_args = args[0]

        if mintmod_class is None:
            raise ValueError("Expected named keyword arg "
                             "mintmod_class in: {}".format(kwargs))

        if mintmod_class == 'MLQuestion':
            classes = ['exercise', 'text']
            attributes = cls._parse_ex_args(
                cmd_args, 'length', 'solution', 'uxid')

        elif mintmod_class == 'MLParsedQuestion':
            classes = ['exercise', 'text']
            attributes = cls._parse_ex_args(cmd_args, 'length', 'solution',
                                            'precision', 'uxid')
            attributes.append(['validator', 'math'])

        elif mintmod_class == 'MLFunctionQuestion':
            classes = ['exercise', 'text']
            attributes = cls._parse_ex_args(
                cmd_args,
                'length',
                'solution',
                'supporting-points',
                'variables',
                'precision',
                'uxid'
            )
            attributes.append(['validator', 'function'])

        elif mintmod_class == 'MLSpecialQuestion':
            classes = ['exercise', 'text']
            attributes = cls._parse_ex_args(
                cmd_args,
                'length',
                'solution',
                'supporting-points',
                'variables',
                'precision',
                'special-type',
                'uxid'
            )

        if oktypes == pf.Block:
            return pf.CodeBlock('', '', classes, attributes)

        return pf.Code('', '', classes, attributes)

    def _parse_ex_args(cmd_args, *names):
        """receive a list of argument names and a list of values and return
        a pandoc conformant argument array containing element's arguments.
        In other words: take a list of arguments and make them named arguments
        for easier referencing."""

        if len(names) != len(cmd_args):
            log('invalid args: %s, args: %s'
                % (names, cmd_args), 'ERROR')
            raise ValueError("Warning: Expected different number of args: {}"
                             .format(cmd_args))

        ret = []
        for idx, name in enumerate(names):
            ret.append([name, cmd_args[idx]])

        return ret

        def _slots_to_json(self):
            return [self._ica_to_json()]



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


def create_header(title_str, doc, level=0, parse_text=False):
    """
    Create a header element.

    Because headers need to be referenced by later elements, references to the
    last found header is remembered.
    """
    if not isinstance(doc, pf.Doc):
        raise ValueError('create_header without Doc element')

    if parse_text:
        title = parse_fragment(title_str)[0].content
    else:
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
