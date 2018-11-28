"""
By default the generated JSON files split text up at each space. This gets
fixed by concatenating the strings and spaces whenever that's possible.

If an array in the generated JSON contains consecutive strings and/or spaces
(as defined in ``TYPES_TO_MERGE``), they get joined to a single element.

**Example**:
``{"t": "Str", "c": "Hello"},{"t": "Space"},{"t": "Str", "c": "World!"}]``
becomes
``{"t": "Str", "c": "Hello World!"}]``

This only happens with *consecutive* array elements *within* the same array. If
there are multiple strings/spaces, followed by any other element, then only the
strings/spaces will be merged. If the other element is followed by more
strings/spaces, these will be merged to a new string. If the other element has
child elements containing strings/spaces, each one will be merged to their own
string
"""

from innoconv.extensions.abstract import AbstractExtension

#: Content Types to be merged - everything but Str is considered whitespace
TYPES_TO_MERGE = ('Space', 'Str', 'SoftBreak')


class JoinStrings(AbstractExtension):
    """This extension concatenates conescutive Strings and Spaces in the ast
    tree"""

    _helptext = "Simplifies strings in the generated JSON files."

    def __init__(self, *args, **kwargs):
        super(JoinStrings, self).__init__(*args, **kwargs)
        self.previous_element = None  # the element we merge to

    # content parsing

    def _process_ast_element(self, ast_element):
        """Process an element form the ast tree, navigating further down
        the tree if possible"""
        self.previous_element = None   # Stop merging on new element
        if isinstance(ast_element, list):
            self._process_ast_array(ast_element)
            return
        try:
            for key in ast_element:
                self._process_ast_element(ast_element[key])
        except TypeError:
            pass

    def _process_ast_array(self, ast_array):
        """The first instance of mergeable content is stored
        in self.previous_element. Every subsequent instance of
        mergeable content gets added to the first instance,
        and finally removed"""
        def is_string_or_space(content_element):
            """Checks if an ast element is mergeable, i.e. string or space"""
            try:
                return content_element['t'] in TYPES_TO_MERGE
            except (TypeError, KeyError):  # could be not a (valid) dictionary
                return False
        self.previous_element = None  # Only merge within one array
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
        self.previous_element = None  # Only merge within one array
        # This last line is necessary for when we finish an array
        # and go back to an array already being squished which contained it

    def _prepare_previous_element(self, content_element):
        """Normalizes self.previous_element to always be a Str"""
        self.previous_element = content_element
        if self.previous_element['t'] != 'Str':
            self.previous_element['t'] = 'Str'
            self.previous_element['c'] = ' '

    def _merge_to_previous_element(self, content_element):
        if content_element['t'] == 'Str':
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

    def post_process_file(self, ast, _):
        """Concatenate the strings and spaces in the ast in-place."""
        self._process_ast_element(ast)

    def post_conversion(self, language):
        """Unused."""

    def finish(self):
        """Unused."""
