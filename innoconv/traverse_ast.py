"""This module helps with traversing an AST."""


class TraverseAst:
    """
    Traverse an AST calling a custom function on each element.

    :param func: Callback for handling an element. Receives element and the
                 parent as parameters.
    :type func: function(dict, dict)
    """

    name_method_map = {
        "BlockQuote": "_under_c",
        "BulletList": "_bulletlist",
        "Code": "_noop",
        "CodeBlock": "_noop",
        "DefinitionList": "_definitionlist",
        "Div": "_under_c_1",
        "Emph": "_under_c",
        "Header": "_header",
        "Image": "_under_c_1",
        "LineBlock": "_lineblock",
        "LineBreak": "_noop",
        "Link": "_under_c_1",
        "Math": "_under_c_1",
        "OrderedList": "_orderedlist",
        "Para": "_under_c",
        "Plain": "_under_c",
        "Quoted": "_under_c_1",
        "RawBlock": "_noop",
        "RawInline": "_noop",
        "SoftBreak": "_noop",
        "Space": "_noop",
        "Span": "_under_c_1",
        "Str": "_noop",
        "Strikeout": "_under_c",
        "Strong": "_under_c",
        "Table": "_table",
    }

    def __init__(self, func):
        """Initialize TraverseAst."""
        self._func = func

    @staticmethod
    def _noop(*_):
        pass

    @staticmethod
    def _unhandled(elem):
        raise ValueError("Unhandled type: {}".format(elem))

    def _under_c(self, elem):
        content = elem["c"]
        if isinstance(content, list):
            self.traverse(elem["c"], elem)
        else:
            self.traverse([elem["c"]], elem)

    def _under_c_1(self, elem):
        self.traverse(elem["c"][1], elem)

    def _header(self, elem):
        self.traverse(elem["c"][2], elem)

    def _orderedlist(self, elem):
        for item in elem["c"][1]:
            self.traverse(item, elem)

    def _bulletlist(self, elem):
        for item in elem["c"]:
            self.traverse(item, elem)

    def _definitionlist(self, elem):
        for item in elem["c"]:
            self.traverse(item[0], elem)
            for node in item[1]:
                self.traverse(node, elem)

    def _lineblock(self, elem):
        for item in elem["c"]:
            self.traverse(item, elem)

    def _table(self, elem):
        for headcell in elem["c"][3]:
            self.traverse(headcell, elem)
        for row in elem["c"][4]:
            for col in row:
                self.traverse(col, elem)

    def _process_children(self, elem):
        """
        Process element children.

        Where children are stored depends on the element type.
        """
        try:
            elem_type = elem["t"]
        except KeyError:
            return
        try:
            getattr(self, self.name_method_map[elem_type])(elem)
        except KeyError:
            self._unhandled(elem)

    def traverse(self, ast, parent=None):
        """
        Traverse an AST calling a function on each element.

        :param ast: Abstract syntax tree to traverse.
        :type ast: list

        :param parent: Parent of current subtree.
        :type parent: dict
        """
        if not isinstance(ast, list):
            return
        for elem in ast:
            self._func(elem, parent)
            self._process_children(elem)
