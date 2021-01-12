"""
Scan documents for index terms.

Viewers may generate a list of words with links to locations in the documents.
In order to achieve this a list of index terms is provided in the
:class:`Manifest <innoconv.manifest.Manifest>` so viewers don't have to scan
the whole documents themselves. Also for every occurence of an index term in
the text an ID is attached.

This extension modifies the AST.

.. note::

  Index terms are not supported in custom pages.
"""

from slugify import slugify

from innoconv.ext.abstract import AbstractExtension
from innoconv.traverse_ast import TraverseAst

INDEX_ATTRIBUTE = "data-index-term"

INDEX_ID_TEMPLATE = "index-term-{}-{}"


class IndexTerms(AbstractExtension):
    """Scan the documents for index terms."""

    _helptext = "Scan the documents for index terms and write them to the manifest."

    def __init__(self, *args, **kwargs):
        """Initialize variables."""
        super().__init__(*args, **kwargs)
        self._current_section_name = None
        self._language = None
        self._index_terms = {}
        self._page_occurences = None

    def _handle_index_term(self, elem, index_term):
        index_term_slug = slugify(index_term)

        # sequentially number IDs per section
        try:
            number = self._page_occurences[index_term_slug] + 1
        except KeyError:
            number = 0
        self._page_occurences[index_term_slug] = number
        occurence_id = INDEX_ID_TEMPLATE.format(index_term_slug, number)
        elem["c"][0][0] = occurence_id

        # add to manifest field
        entry = [
            self._current_section_name,
            f"{index_term_slug}-{number}",
        ]
        try:
            self._index_terms[self._language][index_term_slug][1].append(entry)
        except KeyError:
            self._index_terms[self._language][index_term_slug] = [
                index_term,
                [entry],
            ]

    def process_element(self, elem, _):
        """Respond to AST element."""
        if elem["t"] == "Span":
            attrs = dict(elem["c"][0][2])
            if INDEX_ATTRIBUTE in attrs.keys():
                self._handle_index_term(elem, attrs["data-index-term"])

    def pre_conversion(self, language):
        """Remember current conversion language."""
        self._language = language
        self._index_terms[language] = {}

    def pre_process_file(self, path):
        """Remember current path."""
        self._current_section_name = path[3:]  # strip language
        self._page_occurences = {}

    def post_process_file(
        self, ast, title, content_type, section_type=None, short_title=None
    ):
        """Scan the AST."""
        if content_type == "section":
            TraverseAst(self.process_element).traverse(ast)

    def manifest_fields(self):
        """Add `index_terms` field to manifest."""
        return {"index_terms": self._index_terms}
