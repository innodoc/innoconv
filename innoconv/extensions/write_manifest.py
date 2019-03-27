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
from innoconv.extensions.abstract import AbstractExtension
from innoconv.manifest import ManifestEncoder


class WriteManifest(AbstractExtension):
    """Write a manifest file when conversion is done."""

    _helptext = "Write a {}.json file.".format(MANIFEST_BASENAME)

    def __init__(self, *args, **kwargs):
        """Initialize variables."""
        super(WriteManifest, self).__init__(*args, **kwargs)
        self._output_dir = None

    def _write_manifest(self):
        filename = "{}.json".format(MANIFEST_BASENAME)
        filepath = join(self._output_dir, filename)
        with open(filepath, "w") as out_file:
            json.dump(self._manifest, out_file, cls=ManifestEncoder)
        logging.info("Wrote manifest %s", filepath)

    # extension events

    def start(self, output_dir, _):
        """Remember output directory."""
        self._output_dir = output_dir

    def pre_conversion(self, language):
        """Unused."""

    def pre_process_file(self, path):
        """Unused."""

    def post_process_file(self, _, title):
        """Unused."""

    def post_conversion(self, language):
        """Unused."""

    def finish(self):
        """Output course manifest."""
        self._write_manifest()
