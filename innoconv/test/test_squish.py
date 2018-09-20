"""Unit tests for squish module"""

# pylint: disable=missing-docstring

import unittest

from innoconv.modules.squish.squish import Squish


class TestSquish(unittest.TestCase):

    def __init__(self, arg):
        super(TestSquish, self).__init__(arg)
        self.squish = Squish()

    def _run_test(self, given, expected):
        self.squish.squish(given)
        self.assertEqual(expected, given)

    def test_process_ast(self):
        given = {}
        expected = {}
        self.squish.process_ast(given)
        self.assertEqual(expected, given)

    def test_squish_unchanged(self):
        given = [{"t": "Str", "c": "A"}]
        self._run_test(given[:], given)

        given = [{"t": "Str", "c": "A B"}]
        self._run_test(given[:], given)

        given = []
        self._run_test(given[:], given)

        given = [{"t": "Foo", "c": "Bar"}]
        self._run_test(given[:], given)

        given = [{"t": "Foo", "c": "Bar"},
                 {"t": "Dim", "c": "Sum"}]
        self._run_test(given[:], given)

    def test_squish_str(self):
        given = [{"t": "Str", "c": "A"},
                 {"t": "Str", "c": "B"}]
        expected = [{"t": "Str", "c": "AB"}]
        self._run_test(given, expected)

    def test_squish_space(self):
        given = [{"t": "Space"}]
        expected = [{"t": "Str", "c": " "}]
        self._run_test(given, expected)

        given = [{"t": "Space"},
                 {"t": "Space"}]
        self._run_test(given, expected)

        given = [{"t": "Space"},
                 {"t": "SoftBreak"}]
        self._run_test(given, expected)

        given = [{"t": "Space"},
                 {"t": "Space"},
                 {"t": "Space"},
                 {"t": "Space"}]
        self._run_test(given, expected)

        given = [{"t": "Space"},
                 {"t": "SoftBreak"},
                 {"t": "SoftBreak"},
                 {"t": "Space"},
                 {"t": "Space"},
                 {"t": "SoftBreak"}]
        self._run_test(given, expected)

    def test_squish_complete(self):
        given = [{"t": "Str", "c": "A"},
                 {"t": "Space"},
                 {"t": "Str", "c": "B"}]
        expected = [{"t": "Str", "c": "A B"}]
        self._run_test(given, expected)

        given = [{"t": "Str", "c": "A"},
                 {"t": "Space"},
                 {"t": "Space"},
                 {"t": "Str", "c": "B"},
                 {"t": "Space"},
                 {"t": "Str", "c": "B"}]
        expected = [{"t": "Str", "c": "A B B"}]
        self._run_test(given, expected)

    def test_squish_ignore_unknown(self):
        given = [{"t": "Str", "c": "A"},
                 {"t": "Space"},
                 {"t": "Foo", "c": "Bar"},
                 {"t": "Str", "c": "B"}]
        expected = [{"t": "Str", "c": "A "},
                    {"t": "Foo", "c": "Bar"},
                    {"t": "Str", "c": "B"}]
        self._run_test(given, expected)

        given = [{"t": "Str", "c": "A"},
                 {"t": "Space"},
                 {"t": "Foo", "c": "Bar"},
                 {"t": "Str", "c": "B"},
                 {"t": "Foo", "c": "Bar"}]
        expected = [{"t": "Str", "c": "A "},
                    {"t": "Foo", "c": "Bar"},
                    {"t": "Str", "c": "B"},
                    {"t": "Foo", "c": "Bar"}]
        self._run_test(given, expected)

    def test_nested_json(self):
        given = [{"t": "Strong",
                  "c": [{"t": "Str", "c": "A"}]}]
        self._run_test(given[:], given)

        given = [{"t": "Strong",
                  "c": [{"t": "Str", "c": "A"},
                        {"t": "Space"},
                        {"t": "Str", "c": "B"}]}]
        expected = [{"t": "Strong", "c": [{"t": "Str", "c": "A B"}]}]
        self._run_test(given, expected)

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
        self._run_test(given, expected)

    def test_start_from_obj(self):
        given = {}
        expected = {}
        self._run_test(given, expected)

        given = {"A": "B"}
        expected = {"A": "B"}
        self._run_test(given, expected)

        given = {"t": "A", "c": "B"}
        expected = {"t": "A", "c": "B"}
        self._run_test(given, expected)

        given = {"t": "A", "c": [{}]}
        expected = {"t": "A", "c": [{}]}
        self._run_test(given, expected)

        given = {"t": "A", "c": [{"A": "B"}]}
        expected = {"t": "A", "c": [{"A": "B"}]}
        self._run_test(given, expected)

        given = {"t": "A", "c": [{"t": "Space"}]}
        expected = {"t": "A", "c": [{"t": "Str", "c": " "}]}
        self._run_test(given, expected)

        given = {"t": "A", "c": [{"t": "Str", "c": "A"},
                                 {"t": "Space"}]}
        expected = {"t": "A", "c": [{"t": "Str", "c": "A "}]}
        self._run_test(given, expected)

    def test_special_array(self):
        given = [0, 1, 2]
        self._run_test(given[:], given)

        given = [{'t': 'InlineMath'}, '\\frac12>\\frac23']
        self._run_test(given[:], given)

    def test_special_array2(self):

        given = [
            {
                "c": [
                    1,
                    [
                        "a-2",
                        [],
                        []
                    ],
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
                            [
                                "",
                                [],
                                []
                            ],
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
                                "/handout.txt",
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
                    [
                        "a-2",
                        [],
                        []
                    ],
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
                            [
                                "",
                                [],
                                []
                            ],
                            [
                                {
                                    "c": "B A",
                                    "t": "Str"
                                }
                            ],
                            [
                                "/handout.txt",
                                ""
                            ]
                        ],
                        "t": "Link"
                    }
                ],
                "t": "Para"
            }
        ]
        self._run_test(given, expected)
