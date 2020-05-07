"""Unit tests for innoconv.traverse_ast."""

import unittest
from unittest.mock import call, Mock

from innoconv.traverse_ast import TraverseAst
from .utils import (
    get_bullet_list_ast,
    get_definitionlist_ast,
    get_div_ast,
    get_header_ast,
    get_ordered_list_ast,
    get_para_ast,
    get_table_ast,
)


class TestTraverseAst(unittest.TestCase):
    """Test the TraverseAst class."""

    def setUp(self):
        """Instantiate the runner instance."""
        self._callback_mock = Mock()
        self.traverse_ast = TraverseAst(self._callback_mock)

    def test_traverse(self):
        """Test TraverseAst.traverse method."""
        # pylint: disable=too-many-locals
        ast = [
            get_header_ast(),
            get_div_ast([get_table_ast()]),
            get_ordered_list_ast(),
            get_bullet_list_ast(),
            get_definitionlist_ast(),
        ]
        header = ast[0]
        div = ast[1]
        table = div["c"][1][0]
        table_headcell_0 = table["c"][3][0][0]
        table_headcell_1 = table["c"][3][1][0]
        table_cell_0_0 = table["c"][4][0][0][0]
        table_cell_0_1 = table["c"][4][0][1][0]
        table_cell_1_0 = table["c"][4][1][0][0]
        table_cell_1_1 = table["c"][4][1][1][0]
        olist = ast[2]
        olist_item_0 = olist["c"][1][0][0]
        olist_item_1 = olist["c"][1][1][0]
        blist = ast[3]
        dlist = ast[4]
        expected = (
            (header, None),
            (header["c"][2][0], header),
            (div, None),
            (table, div),
            (table_headcell_0, table),
            (table_headcell_0["c"][0], table_headcell_0),
            (table_headcell_1, table),
            (table_headcell_1["c"][0], table_headcell_1),
            (table_cell_0_0, table),
            (table_cell_0_0["c"][0], table_cell_0_0),
            (table_cell_0_1, table),
            (table_cell_0_1["c"][0], table_cell_0_1),
            (table_cell_1_0, table),
            (table_cell_1_0["c"][0], table_cell_1_0),
            (table_cell_1_1, table),
            (table_cell_1_1["c"][0], table_cell_1_1),
            (olist, None),
            (olist_item_0, olist),
            (olist_item_0["c"][0], olist_item_0),
            (olist_item_1, olist),
            (olist_item_1["c"][0], olist_item_1),
            (blist, None),
            (blist["c"][0][0], blist),
            (blist["c"][0][0]["c"][0], blist["c"][0][0]),
            (blist["c"][1][0], blist),
            (blist["c"][1][0]["c"][0], blist["c"][1][0]),
            (dlist, None),
            (dlist["c"][0][0][0], dlist),
            (dlist["c"][0][1][0][0], dlist),
            (dlist["c"][0][1][0][0]["c"][0], dlist["c"][0][1][0][0]),
            (dlist["c"][1][0][0], dlist),
            (dlist["c"][1][1][0][0], dlist),
            (dlist["c"][1][1][0][0]["c"][0], dlist["c"][0][1][0][0]),
        )
        self.traverse_ast.traverse(ast)
        self.assertEqual(self._callback_mock.call_count, len(expected))
        for idx, exp_elem in enumerate(expected):
            with self.subTest(element=exp_elem):
                call_arg = self._callback_mock.call_args_list[idx]
                self.assertEqual(call_arg, call(*exp_elem))

    def test_error_on_unknown_element(self):
        """Test handling of unknown element."""
        ast = [get_para_ast(content=[{"t": "this-type-does-not-exist", "c": []}])]
        self.traverse_ast.traverse(ast)
        self.assertEqual(self._callback_mock.call_count, 2)
