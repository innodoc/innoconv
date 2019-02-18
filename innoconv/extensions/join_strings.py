"""
This extension modifies the AST. It merges consecutive sequences of strings and
spaces into a single string element.

The motivation behind this extension is to make the AST more readable and also
to save space by compressing the representation. The actual appearance in a
viewer should remain completely untouched.

=======
Example
=======

+--------+----------------------------------------------------------------------+
| Before | ``{"t": "Str", "c": "Foo"},{"t": "Space"},{"t": "Str", "c": "b!"}]`` |
+--------+----------------------------------------------------------------------+
| After  | ``{"t": "Str", "c": "Foo b!"}]``                                     |
+--------+----------------------------------------------------------------------+
"""  # noqa: E501

from innoconv.extensions.abstract import AbstractExtension

#: Type that represents a string
STR_TYPE = 'Str'

#: Content types that are merged
TYPES_TO_MERGE = (STR_TYPE, 'Space', 'SoftBreak')


class JoinStrings(AbstractExtension):
    """This extension merges consecutive strings and spaces in the
    AST."""

    _helptext = "Merge sequences of strings and spaces in the AST."

    def __init__(self, *args, **kwargs):
        super(JoinStrings, self).__init__(*args, **kwargs)
        self.previous_element = None  # the element we merge to

    # content parsing
    def _process_ast_array(self, ast_array):
        """The first instance of mergeable content is stored in
        self.previous_element. Every subsequent instance of mergeable content
        gets added to the first instance and finally removed"""
        def is_string_or_space(content_element):
            """Checks if an ast element is mergeable, i.e. string or space"""
            try:
                return content_element['t'] in TYPES_TO_MERGE
            except (TypeError, KeyError):  # could be an invalid dictionary
                return False

        self.previous_element = None
        index = 0
        while index < len(ast_array):
            ast_element = ast_array[index]
            if is_string_or_space(ast_element):
                if self.previous_element is None:
                    self._prepare_previous_element(ast_element)
                else:
                    self._merge_to_previous_element(ast_element)
                    del ast_array[index]
                    index -= 1
            else:
                self.previous_element = None  # Stop merging on new element
            index += 1

        # Necessary for when we finish an element list and go back to a list
        # that has been processed already which contained it.
        self.previous_element = None

    def _prepare_previous_element(self, content_element):
        """Normalizes self.previous_element to always be a Str"""
        self.previous_element = content_element
        if self.previous_element['t'] != STR_TYPE:
            self.previous_element['t'] = STR_TYPE
            self.previous_element['c'] = ' '

    def _merge_to_previous_element(self, content_element):
        if content_element['t'] == STR_TYPE:
            self.previous_element['c'] += content_element['c']
        else:
            if not self.previous_element['c'].endswith(' '):
                self.previous_element['c'] += ' '

    # extension events

    def start(self, output_dir, source_dir):
        """Unused."""

    def pre_conversion(self, language):
        """Unused."""

    def pre_process_file(self, path):
        """Unused."""

    def process_ast_array(self, ast_array, parent_element):
        """Process AST in-place."""
        self._process_ast_array(ast_array)

    def process_ast_element(self, ast_element, ast_type, parent_element):
        """Unused."""

    def post_process_file(self, ast, _):
        """Unused."""

    def post_conversion(self, language):
        """Unused."""

    def finish(self):
        """Unused."""
