r"""
Handle mintmod LaTeX environments.

.. note::
    Provide a ``handle_ENVNAME`` function for handling ``ENVNAME`` environment.
    You need to `slugify <https://github.com/un33k/python-slugify>`_ the
    environment name.

    Example: ``handle_mxcontent`` method will receive the
    ``\begin{MXContent}…\end{MXContent}`` environment.
"""

import panflute as pf
from innoconv.constants import ELEMENT_CLASSES
from innoconv.errors import NoPrecedingHeader
from innoconv.utils import parse_fragment
from innoconv.mintmod_filter.elements import create_content_box


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
        # Use title from previously found \MSection command
        header = getattr(elem.doc, 'last_header_elem', None)
        if header is None:
            raise NoPrecedingHeader(
                'MSectionStart must precede a header element.')

        div = pf.Div(classes=ELEMENT_CLASSES['MSECTIONSTART'])
        div.content.extend([header] + parse_fragment(elem_content))
        return div

    def handle_mxcontent(self, elem_content, env_args, elem):
        r"""Handle ``\MXContent`` environment."""
        title = env_args[0]
        return create_content_box(
            title, ELEMENT_CLASSES['MXCONTENT'],
            elem_content, elem.doc, level=3, auto_id=True
        )

    def handle_mexercises(self, elem_content, env_args, elem):
        r"""Handle ``\MExercises`` environment."""
        return create_content_box(
            'Aufgaben', ELEMENT_CLASSES['MEXERCISES'],
            elem_content, elem.doc, level=3
        )

    def handle_mexercise(self, elem_content, env_args, elem):
        r"""Handle ``\MExercise`` environment."""
        return create_content_box(
            'Aufgabe', ELEMENT_CLASSES['MEXERCISE'],
            elem_content, elem.doc
        )

    def handle_minfo(self, elem_content, env_args, elem):
        r"""Handle ``\MInfo`` environment."""
        return create_content_box(
            'Info', ELEMENT_CLASSES['MINFO'],
            elem_content, elem.doc
        )

    def handle_mexperiment(self, elem_content, env_args, elem):
        r"""Handle ``\MExperiment`` environment."""
        return create_content_box(
            'Experiment', ELEMENT_CLASSES['MEXPERIMENT'],
            elem_content, elem.doc
        )

    def handle_mexample(self, elem_content, env_args, elem):
        r"""Handle ``\MExample`` command."""
        return create_content_box(
            'Beispiel', ELEMENT_CLASSES['MEXAMPLE'],
            elem_content, elem.doc
        )

    def handle_mhint(self, elem_content, env_args, elem):
        r"""Handle ``\MHint`` command."""
        return create_content_box(
            None, ELEMENT_CLASSES['MHINT'],
            elem_content, elem.doc
        )
