r"""
Handle mintmod LaTeX environments.

.. note::
    Provide a ``handle_ENVNAME`` function for handling ``ENVNAME`` environment.
    You need to `slugify <https://github.com/un33k/python-slugify>`_ the
    environment name.

    Example: ``handle_mxcontent`` method will receive the
    ``\begin{MXContent}…\end{MXContent}`` environment.
"""

from innoconv.constants import ELEMENT_CLASSES, REGEX_PATTERNS
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

    def handle_mcontent(self, elem_content, env_args, elem):
        r"""Handle ``\MContent`` environment."""
        return parse_fragment(elem_content)

    def handle_mintro(self, elem_content, env_args, elem):
        r"""Handle ``\MIntro`` environment."""
        div = create_content_box(elem_content, ELEMENT_CLASSES['MINTRO'])
        title = 'Einführung'  # TODO: I18n
        header = create_header(title, elem.doc, level=3)
        div.content.insert(0, header)
        return div

    ###########################################################################
    # Exercises

    def handle_mexercises(self, elem_content, env_args, elem):
        r"""Handle ``\MExercises`` environment."""
        return create_content_box(elem_content, ELEMENT_CLASSES['MEXERCISES'])

    def handle_mexercise(self, elem_content, env_args, elem):
        r"""Handle ``\MExercise`` environment."""
        return create_content_box(elem_content, ELEMENT_CLASSES['MEXERCISE'])

    def handle_mexerciseitems(self, elem_content, env_args, elem):
        r"""Handle ``\MExerciseitems`` environments by returning an ordered list
        containing the ``\item`` s defined in the environment. This is needed
        on top of handle_itemize as there are also mexerciseitems environments
        outside itemize environments."""
        return self._replace_mexerciseitems(elem)

    ###########################################################################

    def handle_itemize(self, elem_content, env_args, elem):
        r"""Handle itemize environments, that were not correctly recognized by
        pandoc. This e.g. happens if there are ``\MExerciseItems`` environments
        contained in the items."""
        return self._replace_mexerciseitems(elem)

    def handle_minfo(self, elem_content, env_args, elem):
        r"""Handle ``\MInfo`` environment."""
        return create_content_box(elem_content, ELEMENT_CLASSES['MINFO'])

    def handle_mxinfo(self, elem_content, env_args, elem):
        r"""Handle ``\MXInfo`` environment."""
        div = create_content_box(elem_content, ELEMENT_CLASSES['MINFO'])
        header = create_header(env_args[0], elem.doc, level=4, parse_text=True)
        div.content.insert(0, header)
        return div

    def handle_mexperiment(self, elem_content, env_args, elem):
        r"""Handle ``\MExperiment`` environment."""
        return create_content_box(elem_content, ELEMENT_CLASSES['MEXPERIMENT'])

    def handle_mexample(self, elem_content, env_args, elem):
        r"""Handle ``\MExample`` command."""
        return create_content_box(elem_content, ELEMENT_CLASSES['MEXAMPLE'])

    def handle_mhint(self, elem_content, env_args, elem):
        r"""Handle ``\MHint`` command."""
        return create_content_box(elem_content, ELEMENT_CLASSES['MHINT'])

    def handle_mtest(self, elem_content, env_args, elem):
        r"""Handle ``\MTest`` environment."""
        div = create_content_box(elem_content, ELEMENT_CLASSES['MTEST'])

        # remove reference to section
        title = REGEX_PATTERNS['FIX_MTEST'].sub('', env_args[0])

        header = create_header(title, elem.doc, level=3)
        content, identifier = extract_identifier(div.content)
        if identifier:
            div.content = content
            header.identifier = identifier
        div.content.insert(0, header)
        return div

    def handle_mcoshzusatz(self, elem_content, env_args, elem):
        r"""Handle ``\MCOSHZusatz`` environment."""
        return create_content_box(elem_content, ELEMENT_CLASSES['MCOSHZUSATZ'])

    def _replace_mexerciseitems(self, elem):
        r"""Helper function to replace `MExerciseItems` with enumerate in elem
        text and return the pandoc output of the parsed altered element."""
        elem.text = elem.text.replace('\\begin{MExerciseItems}',
                                      '\\begin{enumerate}')
        elem.text = elem.text.replace('\\end{MExerciseItems}',
                                      '\\end{enumerate}')
        return parse_fragment(elem.text)
