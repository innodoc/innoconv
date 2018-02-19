"""Handle mintmod LaTeX environments.

Convention: Provide a `handle_ENVNAME` function for handling `ENVNAME`
            environment. You need to slugify environment name.

Example: `handle_mxcontent` method will receive `MXContent` environment.
"""

import panflute as pf
from slugify import slugify
from mintmod_filter.utils import pandoc_parse, debug

MXCONTENT_CLASSES = ['content']
MEXERCISES_CLASSES = ['content', 'exercises']
MEXERCISE_CLASSES = ['exercise']


class Environments():
    def handle_msectionstart(self, elem_content, env_args, doc):
        """Handle `MSectionStart` environment."""
        # Use title from previously found \MSection command

        header = getattr(doc, "last_header_elem", None)
        if header is None:
            debug("warning handle_msectionstart did not find a previously \
            found header element.")

        div = pf.Div(classes=['section-start'])
        div.content.extend([header] + pandoc_parse(elem_content))
        return div

    def handle_mxcontent(self, elem_content, env_args, doc):
        """Handle `MXContent` environment."""
        title = env_args[0]
        header = pf.Header(
            pf.RawInline(title), identifier=slugify(title), level=3)
        div = pf.Div(classes=MXCONTENT_CLASSES)
        div.content.extend([header] + pandoc_parse(elem_content))
        return div

    def handle_mexercises(self, elem_content, env_args, doc):
        """Handle `MExercises` environment."""
        header = pf.Header(pf.RawInline('Aufgaben'), level=3)  # TODO i18n?
        div = pf.Div(classes=MEXERCISES_CLASSES)
        div.content.extend([header] + pandoc_parse(elem_content))
        return div

    def handle_mexercise(self, elem_content, env_args, doc):
        """Handle `MExercise` environment."""
        header = pf.Header(pf.RawInline('Aufgabe'), level=4)  # TODO i18n?
        div = pf.Div(classes=MEXERCISE_CLASSES)
        div.content.extend([header] + pandoc_parse(elem_content))
        return div
