"""
Scan documents for numbered boxes (info, example, exercise).

Viewers need to be able to quickly number and reference boxes without scanning
the whole document structure themselves. This extension adds a field to the
:class:`Manifest <innoconv.manifest.Manifest>` that lists all boxes per section.

It will assign an auto-generated ``ID`` based on the box type and number to the
box div element (in case it doesn't already have one). Also a ``data-number``
attribute is attached.
"""

import logging
from pathlib import Path

from innoconv.ext.abstract import AbstractExtension
from innoconv.traverse_ast import TraverseAst

BOX_CLASSES = ("example", "info", "exercise")


class NumberBoxes(AbstractExtension):
    """Scan the documents for boxes."""

    _helptext = "Number all boxes and add a boxes field to the manifest."

    def __init__(self, *args, **kwargs):
        """Initialize variables."""
        super(NumberBoxes, self).__init__(*args, **kwargs)
        self._counters = {
            "box": 0,
            "section": 0,
            "subsection": 0,
        }
        self._boxes = {}
        self._language = None
        self._parts = None
        self._done = False
        self._num_boxes = 0

    def _add_box(self, box_type, elem):
        self._counters["box"] += 1
        number = "{section}.{subsection}.{box}".format(**self._counters)
        section_id = "/".join(self._parts)
        box = (number, box_type)

        if self._done:
            # Ensure this language doesn't have extra boxes
            if box not in self._boxes[section_id]:
                logging.warning(
                    "Section %s has extra box %s (%s) for language %s",
                    section_id,
                    number,
                    box_type,
                    self._language,
                )
            self._num_boxes += 1
        else:
            try:
                self._boxes[section_id].append(box)
            except KeyError:
                self._boxes[section_id] = [box]

        # Use type and number as ID for element
        if not elem["c"][0][0]:
            elem["c"][0][0] = "{}-{}".format(box_type, number)

        # Attach number as attribute
        elem["c"][0][2].append(("data-number", number))

    # extension events

    def process_element(self, elem, _):
        """Respond to AST element."""
        if elem["t"] == "Div":
            classes = elem["c"][0][1]
            for box_class in BOX_CLASSES:
                if box_class in classes:
                    self._add_box(box_class, elem)
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

    def post_process_file(self, ast, _, content_type):
        """Scan the AST."""
        if content_type == "section":
            self._num_boxes = 0
            section_level = len(self._parts)
            if section_level > 0:
                if section_level == 1:
                    self._counters["section"] += 1
                    self._counters["subsection"] = 0
                    self._counters["box"] = 0
                elif section_level == 2:
                    self._counters["subsection"] += 1
                    self._counters["box"] = 0

                TraverseAst(self.process_element).traverse(ast)

                # Ensure this language doesn't have less boxes in section
                if self._done:
                    section_id = "/".join(self._parts)
                    try:
                        expected_len = len(self._boxes[section_id])
                    except KeyError:
                        expected_len = 0
                    if expected_len > self._num_boxes:
                        logging.warning(
                            "Section %s has too few boxes for language %s",
                            section_id,
                            self._language,
                        )

    def manifest_fields(self):
        """Add ``boxes`` field to manifest."""
        return {"boxes": self._boxes}
