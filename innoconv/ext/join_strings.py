"""
Merge consecutive sequences of strings and spaces into a single string element.

The motivation behind this extension is to make the AST more readable and also
to save space by compressing the representation. The actual appearance in a
viewer remains identical.

This extension modifies the AST.

=======
Example
=======

``{"t":"Str","c":"Foo"},{"t":"Space"},{"t":"Str","c":"bar"}]`` →
``{"t":"Str","c":"Foo bar"}]``
"""

from innoconv.ext.abstract import AbstractExtension

#: Type that represents a string
STR_TYPE = "Str"

#: Content types that are merged
TYPES_TO_MERGE = (STR_TYPE, "Space", "SoftBreak")


class JoinStrings(AbstractExtension):
    """Merge consecutive strings and spaces in the AST."""

    _helptext = "Merge sequences of strings and spaces in the AST."

    def __init__(self, *args, **kwargs):
        """Initialize variables."""
        super().__init__(*args, **kwargs)
        self.previous_element = None  # the element we merge to

    # content parsing

    def _process_ast_element(self, ast_element):
        """
        Process a single element in the AST.

        Descend further down if possible.
        """
        self.previous_element = None  # Stop merging on new element
        if isinstance(ast_element, list):
            self._process_ast_array(ast_element)
            return
        try:
            for key in ast_element:
                self._process_ast_element(ast_element[key])
        except TypeError:
            pass

    def _process_ast_array(self, ast_array):
        """
        Iterate over elements in AST.

        The first instance of mergeable content is stored in
        self.previous_element. Every subsequent instance of mergeable content
        gets added to the first instance and finally removed.
        """

        def is_string_or_space(content_element):
            """Check if an ast element is mergeable, i.e. String or Space."""
            try:
                return content_element["t"] in TYPES_TO_MERGE
            except (TypeError, KeyError):  # could be an invalid dictionary
                return False

        self.previous_element = None
        to_delete = set()
        for pos, ast_element in enumerate(ast_array):
            if is_string_or_space(ast_element):
                if self.previous_element is None:
                    self._prepare_previous_element(ast_element)
                else:
                    self._merge_to_previous_element(ast_element)
                    to_delete.add(pos)
            else:
                self._process_ast_element(ast_element)
        removed_items = 0  # remember number of deleted items to adjust index
        for index in to_delete:
            del ast_array[index - removed_items]
            removed_items += 1
        # Necessary for when we finish an element list and go back to a list
        # that has been processed already which contained it.
        self.previous_element = None

    def _prepare_previous_element(self, content_element):
        """Normalize self.previous_element to always be a Str."""
        self.previous_element = content_element
        if self.previous_element["t"] != STR_TYPE:
            self.previous_element["t"] = STR_TYPE
            self.previous_element["c"] = " "

    def _merge_to_previous_element(self, content_element):
        if content_element["t"] == STR_TYPE:
            self.previous_element["c"] += content_element["c"]
        else:
            if not self.previous_element["c"].endswith(" "):
                self.previous_element["c"] += " "

    # extension events

    def post_process_file(
        self, ast, title, content_type, section_type=None, short_title=None
    ):
        """Process AST in-place."""
        self._process_ast_element(ast)
