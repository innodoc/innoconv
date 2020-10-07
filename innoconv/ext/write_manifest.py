"""
Extension that writes a :file:`manifest.json` to the output folder.

Every course needs a :class:`Manifest <innoconv.manifest.Manifest>`.
Additionally to the fields from the source manifest it can include a table of
contents and a glossary.
"""

import json
import logging
from os.path import join

from innoconv.constants import MANIFEST_BASENAME
from innoconv.ext.abstract import AbstractExtension
from innoconv.manifest import Manifest


class WriteManifest(AbstractExtension):
    """Write a manifest file when conversion is done."""

    _helptext = f"Write a {MANIFEST_BASENAME}.json file."

    def __init__(self, *args, **kwargs):
        """Initialize variables."""
        super().__init__(*args, **kwargs)
        self._output_dir = None

    def _write_manifest(self):
        manifest_dict = {}
        for field in Manifest.required_fields:
            manifest_dict[field] = getattr(self._manifest, field)
        # optional fields
        for field in Manifest.optional_fields:
            try:
                manifest_dict[field] = getattr(self._manifest, field)
            except AttributeError:
                pass
        # extra fields from extensions
        for ext in self._extensions:
            try:
                manifest_dict.update(ext.manifest_fields())
            except AttributeError:
                pass
        # write file
        filename = f"{MANIFEST_BASENAME}.json"
        filepath = join(self._output_dir, filename)
        with open(filepath, "w") as out_file:
            json.dump(manifest_dict, out_file)
        logging.info("Wrote manifest %s", filepath)

    # extension events

    def start(self, output_dir, _):
        """Remember output directory."""
        self._output_dir = output_dir

    def finish(self):
        """Output course manifest."""
        self._write_manifest()
