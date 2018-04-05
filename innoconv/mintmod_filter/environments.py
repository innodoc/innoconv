r"""
Handle mintmod LaTeX environments.

.. note::
    Provide a ``handle_ENVNAME`` function for handling ``ENVNAME`` environment.
    You need to `slugify <https://github.com/un33k/python-slugify>`_ the
    environment name.

    Example: ``handle_mxcontent`` method will receive the
    ``\begin{MXContent}…\end{MXContent}`` environment.
"""

from innoconv.constants import ELEMENT_CLASSES
from innoconv.mintmod_filter.elements import create_content_box, create_header
from innoconv.utils import parse_fragment, extract_identifier


class Environments():

    r"""Handlers for environments are defined here.

    Given the environment:

    .. code-block:: latex

        \begin{MXContent}{Foo title long}{Foo title}{STD}
            Foo content
        \end{MXContent}

    The handler method ``handle_mxcontent`` receives the following arguments:

    .. hlist::
        :columns: 1

        * ``elem_content``: ``'Foo content'``
        * ``cmd_args``: ``['Foo title long', 'Foo title', 'STD']``
        * ``elem``: :class:`panflute.elements.RawBlock`
    """

    # pylint: disable=unused-argument,no-self-use

    def handle_msectionstart(self, elem_content, env_args, elem):
        r"""Handle ``\MSectionStart`` environment."""
        return parse_fragment(elem_content)

    def handle_mxcontent(self, elem_content, env_args, elem):
        r"""Handle ``\MXContent`` environment."""
        content = parse_fragment(elem_content)
        header = create_header(env_args[0], elem.doc, level=3)
        content, identifier = extract_identifier(content)
        if identifier:
            header.identifier = identifier
        content.insert(0, header)
        return content

    def handle_mintro(self, elem_content, env_args, elem):
        r"""Handle ``\MIntro`` environment."""
        div = create_content_box(elem_content, ELEMENT_CLASSES['MINTRO'])
        title = 'Einführung'  # TODO: I18n
        header = create_header(title, elem.doc, level=3)
        div.content.insert(0, header)
        return div

    def handle_mexercises(self, elem_content, env_args, elem):
        r"""Handle ``\MExercises`` environment."""
        return create_content_box(elem_content, ELEMENT_CLASSES['MEXERCISES'])

    def handle_mexercise(self, elem_content, env_args, elem):
        r"""Handle ``\MExercise`` environment."""
        return create_content_box(elem_content, ELEMENT_CLASSES['MEXERCISE'])

    def handle_minfo(self, elem_content, env_args, elem):
        r"""Handle ``\MInfo`` environment."""
        return create_content_box(elem_content, ELEMENT_CLASSES['MINFO'])

    def handle_mexperiment(self, elem_content, env_args, elem):
        r"""Handle ``\MExperiment`` environment."""
        return create_content_box(elem_content, ELEMENT_CLASSES['MEXPERIMENT'])

    def handle_mexample(self, elem_content, env_args, elem):
        r"""Handle ``\MExample`` command."""
        return create_content_box(elem_content, ELEMENT_CLASSES['MEXAMPLE'])

    def handle_mhint(self, elem_content, env_args, elem):
        r"""Handle ``\MHint`` command."""
        return create_content_box(elem_content, ELEMENT_CLASSES['MHINT'])
