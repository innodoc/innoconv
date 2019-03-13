"""Unit tests for join_strings module"""

# pylint: disable=missing-docstring

from innoconv.extensions.join_strings import JoinStrings
from innoconv.test.extensions import TestExtension

PATHS = (
    ("Foo", ('foo',)),
)


class TestJoinStrings(TestExtension):
    @staticmethod
    def _run(extension=JoinStrings, ast=None, languages=('en',), paths=PATHS):
        _, [ast] = TestExtension._run(
            extension, ast, languages=languages, paths=paths)
        return ast

    def test_unchanged(self):
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
                ast = self._run(ast=given)
                self.assertEqual(ast, given)

    def test_str(self):
        given = [{"t": "Str", "c": "A"},
                 {"t": "Str", "c": "B"}]
        ast = self._run(ast=given)
        self.assertEqual(ast, [{"t": "Str", "c": "AB"}])

    def test_space(self):
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
                ast = self._run(ast=given)
                self.assertEqual(ast, expected)

    def test_complete_a(self):
        given = [{"t": "Str", "c": "A"},
                 {"t": "Space"},
                 {"t": "Str", "c": "B"}]
        ast = self._run(JoinStrings, given)
        self.assertEqual(ast, [{"t": "Str", "c": "A B"}])

    def test_complete_b(self):
        given = [{"t": "Str", "c": "A"},
                 {"t": "Space"},
                 {"t": "Space"},
                 {"t": "Str", "c": "B"},
                 {"t": "Space"},
                 {"t": "Str", "c": "B"}]
        ast = self._run(ast=given)
        self.assertEqual(ast, [{"t": "Str", "c": "A B B"}])

    def test_ignore_unknown_a(self):
        given = [{"t": "Str", "c": "A"},
                 {"t": "Space"},
                 {"t": "Foo", "c": "Bar"},
                 {"t": "Str", "c": "B"}]
        expected = [{"t": "Str", "c": "A "},
                    {"t": "Foo", "c": "Bar"},
                    {"t": "Str", "c": "B"}]
        ast = self._run(ast=given)
        self.assertEqual(ast, expected)

    def test_ignore_unknown_b(self):
        given = [{"t": "Str", "c": "A"},
                 {"t": "Space"},
                 {"t": "Foo", "c": "Bar"},
                 {"t": "Str", "c": "B"},
                 {"t": "Foo", "c": "Bar"}]
        expected = [{"t": "Str", "c": "A "},
                    {"t": "Foo", "c": "Bar"},
                    {"t": "Str", "c": "B"},
                    {"t": "Foo", "c": "Bar"}]
        ast = self._run(ast=given)
        self.assertEqual(ast, expected)

    def test_nested_json(self):
        given = [{"t": "Strong",
                  "c": [{"t": "Str", "c": "A"},
                        {"t": "Space"},
                        {"t": "Str", "c": "B"}]}]
        expected = [{"t": "Strong", "c": [{"t": "Str", "c": "A B"}]}]
        ast = self._run(ast=given)
        self.assertEqual(ast, expected)

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
        ast = self._run(ast=given)
        self.assertEqual(ast, expected)

    def test_special_array(self):
        """Collection of simple special cases found in actual conversions"""
        examples = (
            [0, 1, 2],
            [{'t': 'InlineMath'}, '\\frac12>\\frac23']
        )
        for given in examples:
            with self.subTest(given):
                ast = self._run(ast=given)
                self.assertEqual(ast, given)

    def test_special_array2(self):
        """Problematic case found in actual conversions"""
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
        ast = self._run(ast=given)
        self.assertEqual(ast, expected)
