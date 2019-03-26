"""
The manifest comprises course metadata.

A ``manifest.yml`` file needs to exist in every course content and resided at
the content root directory. It is usually written by hand.

There is also a representation in the JSON format. It is generated
automatically by the converter and additionally includes the table of contents
that is generated from the section structure. It can be found in the output
folder.

Example
=======

.. code-block:: yaml

   title:
     en: Example title
     de: Beispiel-Titel
   languages: en,de
"""

import json
import os

import yaml

from innoconv.constants import MANIFEST_BASENAME


class Manifest:
    """Represents course metadata."""

    required_fields = ("title", "languages")
    optional_fields = ("keywords", "custom_content")

    def __init__(self, data):
        """
        Initialize a manifest.

        :param data: A dict with the manifest fields as keys
        :type data: dict
        """
        for field in self.required_fields:
            try:
                setattr(self, field, data[field])
            except KeyError:
                msg = "Required field {} not found in manifest!".format(field)
                raise RuntimeError(msg)
        for field in self.optional_fields:
            try:
                setattr(self, field, data[field])
            except KeyError:
                pass
        self.toc = []

    @classmethod
    def from_directory(cls, dirpath):
        """
        Read manifest from content directory.

        :param dirpath: Full path to content directory.
        :type dirpath: str

        :rtype: Manifest
        :returns: Manifest object
        """

        def _read_manifest_data(file_ext):
            filename = "{}.{}".format(MANIFEST_BASENAME, file_ext)
            with open(os.path.join(dirpath, filename), "r") as file:
                return file.read()

        try:
            manifest_data = _read_manifest_data("yml")
        except FileNotFoundError:
            manifest_data = _read_manifest_data("yaml")
        return cls.from_yaml(manifest_data)

    @classmethod
    def from_yaml(cls, yaml_data):
        """
        Create a manifest from YAML data.

        :param yaml_data: YAML representation of a manifest
        :type yaml_data: str

        :rtype: Manifest
        :returns: Manifest object
        """
        data = yaml.safe_load(yaml_data)
        return Manifest(data)


class ManifestEncoder(json.JSONEncoder):
    """JSON encoder that can handle Manifest objects."""

    def default(self, o):
        """Return dict for Manifest objects."""
        # pylint: disable=method-hidden
        # https://github.com/PyCQA/pylint/issues/414
        if isinstance(o, Manifest):
            manifest_dict = {}
            # required fields
            for field in Manifest.required_fields:
                manifest_dict[field] = getattr(o, field)
            # optional fields
            for field in Manifest.optional_fields:
                try:
                    manifest_dict[field] = getattr(o, field)
                except AttributeError:
                    pass
            # extra fields
            manifest_dict["toc"] = o.toc
            return manifest_dict
        return super(ManifestEncoder, self).default(o)
