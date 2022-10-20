"""
Scan documents for numbered cards (info, example, exercise).

Viewers need to be able to quickly number and reference cards without scanning
the whole document structure themselves. This extension adds a field to the
:class:`Manifest <innoconv.manifest.Manifest>` that lists all cards per section.

It will assign an auto-generated ``ID`` based on the card type and number to the
card div element (in case it doesn't already have one). Also a ``data-number``
attribute is attached.

Furthermore this extension faciliates the course-wide tracking of exercise
progress. For each exercise, the total achievable points and number of questions
are stored. A viewer application can easily display total points per section
without having to scan all documents for exercises.
"""

import logging
from pathlib import Path

from innoconv.ext.abstract import AbstractExtension
from innoconv.traverse_ast import IgnoreSubtreeError, TraverseAst

CARD_CLASSES = ("example", "info", "exercise")


class NumberCards(AbstractExtension):
    """Scan the documents for cards."""

    _helptext = "Number all cards and add a cards field to the manifest."

    def __init__(self, *args, **kwargs):
        """Initialize variables."""
        super().__init__(*args, **kwargs)
        self._counters = {
            "card": 0,
            "section": 0,
            "subsection": 0,
        }
        self._cards = {}
        self._language = None
        self._parts = None
        self._done = False
        self._counters = {
            "card_count": 0,
            "exercise_points": 0,
            "question_count": 0,
        }

    def _add_card(self, card_type, elem):
        self._counters["card"] += 1
        number = "{section}.{subsection}.{card}".format(**self._counters)
        section_id = "/".join(self._parts)
        if elem["c"][0][0]:
            card_id = elem["c"][0][0]
        else:
            card_id = f"{card_type}-{number}"
            if card_type == "exercise":
                logging.warning(
                    "Section %s has exercise without ID: %s for language %s",
                    section_id,
                    number,
                    self._language,
                )

        # Collect questions inside exercise to get total points, question count
        if card_type == "exercise":
            self._counters["exercise_points"] = 0
            self._counters["question_count"] = 0
            TraverseAst(self._scan_questions).traverse([elem])
            card = (
                card_id,
                number,
                card_type,
                self._counters["exercise_points"],
                self._counters["question_count"],
            )
        else:
            card = (card_id, number, card_type)

        if self._done:
            # Ensure this language doesn't have extra cards
            if section_id not in self._cards:
                self._cards[section_id] = []
            if card not in self._cards[section_id]:
                logging.warning(
                    "Section %s has extra card %s (%s) for language %s",
                    section_id,
                    number,
                    card_type,
                    self._language,
                )
            self._counters["card_count"] += 1
        else:
            try:
                self._cards[section_id].append(card)
            except KeyError:
                self._cards[section_id] = [card]

        # Set ID
        if not elem["c"][0][0]:
            elem["c"][0][0] = card_id

        # Attach number as attribute
        elem["c"][0][2].append(("data-number", number))

    def _scan_questions(self, elem, _):
        if elem["t"] == "Span" and "question" in elem["c"][0][1]:
            self._counters["question_count"] += 1
            for key, val in elem["c"][0][2]:
                if key == "points":
                    try:
                        self._counters["exercise_points"] += int(val)
                    except ValueError:
                        msg = "Got bad int value for question point attribute: %s"
                        logging.warning(msg, val)

    # extension events

    def process_element(self, elem, _):
        """Respond to AST element."""
        if elem["t"] == "Div":
            classes = elem["c"][0][1]
            for card_class in CARD_CLASSES:
                if card_class in classes:
                    self._add_card(card_class, elem)
                    if card_class == "exercise":
                        raise IgnoreSubtreeError
                    break

    def pre_conversion(self, language):
        """Remember current conversion language."""
        self._counters["section"] = 0
        self._counters["subsection"] = 0
        self._language = language

    def post_conversion(self, _):
        """Set scan to done."""
        self._done = True

    def pre_process_file(self, path):
        """Remember current path."""
        self._parts = Path(path).parts[1:]  # strip language folder

    def post_process_file(
        self, ast, title, content_type, section_type=None, short_title=None
    ):
        """Scan the AST."""
        if content_type == "section":
            self._counters["card_count"] = 0
            section_level = len(self._parts)
            if section_level > 0:
                if section_level == 1:
                    self._counters["section"] += 1
                    self._counters["subsection"] = 0
                    self._counters["card"] = 0
                elif section_level == 2:
                    self._counters["subsection"] += 1
                    self._counters["card"] = 0

                TraverseAst(self.process_element).traverse(ast)

                # Ensure this language doesn't have less cards in section
                if self._done:
                    section_id = "/".join(self._parts)
                    try:
                        expected_len = len(self._cards[section_id])
                    except KeyError:
                        expected_len = 0
                    if expected_len > self._counters["card_count"]:
                        logging.warning(
                            "Section %s has too few cards for language %s",
                            section_id,
                            self._language,
                        )

    def manifest_fields(self):
        """Add ``cards`` field to manifest."""
        return {"cards": self._cards}
