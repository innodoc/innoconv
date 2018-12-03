"""Unit tests for join_strings module"""

# pylint: disable=missing-docstring

import copy

from innoconv.extensions.join_strings import JoinStrings
from innoconv.test.extensions import TestExtension
from innoconv.test.utils import get_tricky_ast_parts

PATHS = (
    ("Foo", ('foo',)),
)


class TestJoinStrings(TestExtension):
    @staticmethod
    def _run(extension, ast=None, languages=('en',), paths=PATHS,
             file_title=None):
        return TestExtension._run(
            extension, ast, paths=paths, languages=languages,
            file_title=file_title)

    def test_join_strings_unchanged(self):
        examples = (
            [{"t": "Str", "c": "A"}],
            [{"t": "Str", "c": "A B"}],
            [],
            [{"t": "Foo", "c": "Bar"}],
            [{"t": "Foo", "c": "Bar"}, {"t": "Dim", "c": "Sum"}],
            [[]],
            [{}],
            [{"t": "Foo", "c": []}],
            [{"t": "Foo", "c": [{"t": "Str", "c": "A"}]}],
            {}
        )
        for given in examples:
            with self.subTest(given):
                expected = copy.deepcopy(given)
                self._run(JoinStrings, given)
                self.assertEqual(expected, given)

    def test_join_strings_str(self):
        given = [{"t": "Str", "c": "A"},
                 {"t": "Str", "c": "B"}]
        expected = [{"t": "Str", "c": "AB"}]
        self._run(JoinStrings, given)
        self.assertEqual(expected, given)

    def test_join_strings_space(self):
        examples = (
            [{"t": "Space"}],
            [{"t": "Space"}, {"t": "Space"}],
            [{"t": "Space"}, {"t": "SoftBreak"}],
            [{"t": "Space"}, {"t": "Space"}, {"t": "Space"}, {"t": "Space"}],
            [{"t": "Space"}, {"t": "SoftBreak"}, {"t": "SoftBreak"}],
            [{"t": "SoftBreak"}, {"t": "SoftBreak"}, {"t": "SoftBreak"}],
            [{"t": "SoftBreak"}, {"t": "Space"}, {"t": "SoftBreak"}],
            [{"t": "SoftBreak"}],
            [{"t": "Str", "c": " "}],
            [{"t": "Str", "c": " "}, {"t": "Space"}],
            [{"t": "Str", "c": " "}, {"t": "SoftBreak"}],
        )
        expected = [{"t": "Str", "c": " "}]
        for given in examples:
            with self.subTest(given):
                self._run(JoinStrings, given)
                self.assertEqual(expected, given)

    def test_join_strings_complete_a(self):
        given = [{"t": "Str", "c": "A"},
                 {"t": "Space"},
                 {"t": "Str", "c": "B"}]
        expected = [{"t": "Str", "c": "A B"}]
        self._run(JoinStrings, given)
        self.assertEqual(expected, given)

    def test_join_strings_title(self):
        given = [{"t": "Str", "c": "A"},
                 {"t": "Space"},
                 {"t": "Str", "c": "B"}]
        expected = [{"t": "Str", "c": "A B"}]
        self._run(JoinStrings, file_title=given)
        self.assertEqual(expected, given)

    def test_join_strings_complete_b(self):
        given = [{"t": "Str", "c": "A"},
                 {"t": "Space"},
                 {"t": "Space"},
                 {"t": "Str", "c": "B"},
                 {"t": "Space"},
                 {"t": "Str", "c": "B"}]
        expected = [{"t": "Str", "c": "A B B"}]
        self._run(JoinStrings, given)
        self.assertEqual(expected, given)

    def test_join_strings_ignore_unknown_a(self):
        given = [{"t": "Str", "c": "A"},
                 {"t": "Space"},
                 {"t": "Foo", "c": "Bar"},
                 {"t": "Str", "c": "B"}]
        expected = [{"t": "Str", "c": "A "},
                    {"t": "Foo", "c": "Bar"},
                    {"t": "Str", "c": "B"}]
        self._run(JoinStrings, given)
        self.assertEqual(expected, given)

    def test_join_strings_ignore_unknown_b(self):
        given = [{"t": "Str", "c": "A"},
                 {"t": "Space"},
                 {"t": "Foo", "c": "Bar"},
                 {"t": "Str", "c": "B"},
                 {"t": "Foo", "c": "Bar"}]
        expected = [{"t": "Str", "c": "A "},
                    {"t": "Foo", "c": "Bar"},
                    {"t": "Str", "c": "B"},
                    {"t": "Foo", "c": "Bar"}]
        self._run(JoinStrings, given)
        self.assertEqual(expected, given)

    def test_nested_json(self):
        given = [{"t": "Strong",
                  "c": [{"t": "Str", "c": "A"},
                        {"t": "Space"},
                        {"t": "Str", "c": "B"}]}]
        expected = [{"t": "Strong", "c": [{"t": "Str", "c": "A B"}]}]
        self._run(JoinStrings, given)
        self.assertEqual(expected, given)

    def test_nested_json_complete(self):
        given = [{"t": "Str", "c": "A"},
                 {"t": "Space"},
                 {"t": "Strong",
                  "c": [{"t": "Str", "c": "A"},
                        {"t": "Space"},
                        {"t": "Strong",
                         "c": [{"t": "Str", "c": "A"},
                               {"t": "Space"},
                               {"t": "Foo", "c": "Bar"},
                               {"t": "Str", "c": "B"}]},
                        {"t": "Space"},
                        {"t": "Str", "c": "B"}]}]
        expected = [{"t": "Str", "c": "A "},
                    {"t": "Strong",
                     "c": [{"t": "Str", "c": "A "},
                           {"t": "Strong",
                            "c": [{"t": "Str", "c": "A "},
                                  {"t": "Foo", "c": "Bar"},
                                  {"t": "Str", "c": "B"}]},
                           {"t": "Str", "c": " B"}]}]
        self._run(JoinStrings, given)
        self.assertEqual(expected, given)

    def test_special_array(self):
        # Collection of simple special cases found in actual conversions
        for given in get_tricky_ast_parts():
            with self.subTest(given):
                expected = copy.deepcopy(given)
                self._run(JoinStrings, given)
                self.assertEqual(expected, given)

    def test_special_array2(self):
        # Problematic case found in actual conversions
        given = [
            {
                "c": [
                    1,
                    ["a-2", [], []],
                    [
                        {
                            "c": "A",
                            "t": "Str"
                        },
                        {
                            "t": "Space"
                        },
                        {
                            "c": "B",
                            "t": "Str"
                        }
                    ]
                ],
                "t": "Header"
            },
            {
                "c": [
                    {
                        "c": [
                            ["", [], []],
                            [
                                {
                                    "c": "B",
                                    "t": "Str"
                                },
                                {
                                    "t": "Space"
                                },
                                {
                                    "c": "A",
                                    "t": "Str"
                                }
                            ],
                            [
                                "/x.txt",
                                ""
                            ]
                        ],
                        "t": "Link"
                    }
                ],
                "t": "Para"
            }
        ]
        expected = [
            {
                "c": [
                    1,
                    ["a-2", [], []],
                    [
                        {
                            "c": "A B",
                            "t": "Str"
                        }
                    ]
                ],
                "t": "Header"
            },
            {
                "c": [
                    {
                        "c": [
                            ["", [], []],
                            [
                                {
                                    "c": "B A",
                                    "t": "Str"
                                }
                            ],
                            [
                                "/x.txt",
                                ""
                            ]
                        ],
                        "t": "Link"
                    }
                ],
                "t": "Para"
            }
        ]
        self._run(JoinStrings, given)
        self.assertEqual(expected, given)
