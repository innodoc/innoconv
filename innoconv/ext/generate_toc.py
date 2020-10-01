"""
Extension that generates a table of contents.

A table of contents is generated from the course sections and added to the
:class:`Manifest <innoconv.manifest.Manifest>`.
"""

from os.path import split

from innoconv.ext.abstract import AbstractExtension


class GenerateToc(AbstractExtension):
    """Generate a TOC from content sections."""

    _helptext = "Generate a table of contents."

    def __init__(self, *args, **kwargs):
        """Initialize variables."""
        super().__init__(*args, **kwargs)
        self._output_dir = None
        self._current_path = None
        self._language = None
        self._toc = []

    def _add_to_toc(self, title, section_type):
        path_components = self._splitall(self._current_path)
        path_components.pop(0)  # language folder
        if not path_components:  # skip root section
            return
        children = self._toc
        while True:
            path_component = path_components.pop(0)
            child = None
            for check_child in children:
                if check_child["id"] == path_component:
                    child = check_child
                    break
            if not child:
                child = {"id": path_component, "title": {}}
                children.append(child)
            if path_components and "children" not in child:
                # add children list, except in leaf nodes
                child["children"] = []
            if path_components:
                children = child["children"]
            else:
                break

        child["title"][self._language] = title
        if section_type:
            child["type"] = section_type

    @staticmethod
    def _splitall(path):
        """Split path into directory components."""
        all_parts = []
        while True:
            parts = split(path)
            if parts[1] == path:
                all_parts.insert(0, parts[1])
                break
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

    def post_process_file(self, _, title, content_type, section_type=None):
        """Add this section file to the TOC."""
        if content_type == "section":
            self._add_to_toc(title, section_type)

    def manifest_fields(self):
        """Add `toc` field to manifest."""
        return {"toc": self._toc}
