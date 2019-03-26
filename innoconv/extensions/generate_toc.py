"""
Extension that generates a table of contents.

A table of contents is generated from the course sections and added to the
:class:`Manifest <innoconv.manifest.Manifest>`.
"""

from os.path import split

from innoconv.extensions.abstract import AbstractExtension


class GenerateToc(AbstractExtension):
    """Generate a TOC from content sections."""

    _helptext = "Generate a table of contents."

    def __init__(self, *args, **kwargs):
        """Initialize variables."""
        super(GenerateToc, self).__init__(*args, **kwargs)
        self._output_dir = None
        self._current_path = None
        self._language = None

    def _add_to_toc(self, title):
        path_components = self._splitall(self._current_path)
        path_components.pop(0)  # language folder
        if not path_components:  # skip root section
            return
        children = self._manifest.toc
        while path_components:
            section_id = path_components.pop(0)
            # find/create child leaf
            found = None
            for child in children:
                if child["id"] == section_id:
                    found = child
                    try:
                        children = child["children"]
                    except KeyError:
                        children = child["children"] = []
                        break
            # arrived at leaf -> add section
            if not found:
                children.append(
                    {"id": section_id, "title": {self._language: title}}
                )
        if found:
            found["title"][self._language] = title

    @staticmethod
    def _splitall(path):
        """Split path into directory components."""
        all_parts = []
        while 1:
            parts = split(path)
            if parts[1] == path:
                all_parts.insert(0, parts[1])
                break
            else:
                path = parts[0]
                all_parts.insert(0, parts[1])
        return all_parts

    # extension events

    def start(self, output_dir, _):
        """Remember output directory."""
        self._output_dir = output_dir

    def pre_conversion(self, language):
        """Remember current conversion language."""
        self._language = language

    def pre_process_file(self, path):
        """Remember current path."""
        self._current_path = path

    def post_process_file(self, _, title):
        """Add this section file to the TOC."""
        self._add_to_toc(title)

    def post_conversion(self, language):
        """Unused."""

    def finish(self):
        """Unused."""
