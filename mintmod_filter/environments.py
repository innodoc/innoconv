r"""Handle mintmod LaTeX environments.

Convention: Provide a ``handle_ENVNAME`` function for handling ``ENVNAME``
environment. You need to slugify the environment name.

Example: ``handle_mxcontent`` method will receive the
``\begin{MXContent}…\end{MXContent}`` environment.
"""

import panflute as pf
from mintmod_filter.constants import CSS_CLASSES
from mintmod_filter.utils import pandoc_parse, debug, destringify
from mintmod_filter.elements import create_content_box


class Environments():
    def handle_msectionstart(self, elem_content, env_args, doc):
        """Handle ``MSectionStart`` environment."""
        # Use title from previously found \MSection command
        header = getattr(doc, "last_header_elem", None)
        if header is None:
            debug("warning handle_msectionstart did not find a previously \
            found header element.")

        div = pf.Div(classes=['section-start'])
        div.content.extend([header] + pandoc_parse(elem_content))
        return div

    def handle_mxcontent(self, elem_content, env_args, doc):
        """Handle ``MXContent`` environment."""
        title = env_args[0]
        return create_content_box(
            title, CSS_CLASSES['MXCONTENT'],
            elem_content, doc, level=3, auto_id=True
        )

    def handle_mexercises(self, elem_content, env_args, doc):
        """Handle ``MExercises`` environment."""
        return create_content_box(
            'Aufgaben', CSS_CLASSES['MEXERCISES'],
            elem_content, doc, level=3
        )

    def handle_mexercise(self, elem_content, env_args, doc):
        """Handle ``MExercise`` environment."""
        return create_content_box(
            'Aufgabe', CSS_CLASSES['MEXERCISE'],
            elem_content, doc
        )

    def handle_minfo(self, elem_content, env_args, doc):
        """Handle ``MInfo`` environment."""
        return create_content_box(
            'Info', CSS_CLASSES['MINFO'],
            elem_content, doc
        )

    def handle_mexperiment(self, elem_content, env_args, doc):
        """Handle ``MExperiment`` environment."""
        return create_content_box(
            'Experiment', CSS_CLASSES['MEXPERIMENT'],
            elem_content, doc
        )

    def handle_mexample(self, elem_content, env_args, doc):
        """Handle ``MExample`` command."""
        return create_content_box(
            'Beispiel', CSS_CLASSES['MEXAMPLE'],
            elem_content, doc
        )

    def handle_mhint(self, elem_content, env_args, doc):
        """Handle ``MHint`` command."""
        div = pf.Div(classes=CSS_CLASSES['MHINT'])

        div.content.extend([
            pf.Plain(pf.Span(*destringify(env_args[0]),
                             classes=CSS_CLASSES['MHINT_TEXT']))
        ] + pandoc_parse(elem_content))

        return div
