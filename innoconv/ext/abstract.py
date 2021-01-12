"""
Base class for all other extensions.

The AbstractExtension is not instantiated directly but serves as super-class to
all extensions.
"""


class AbstractExtension:
    """
    Abstract class for extensions.

    The class all extensions inherit from. The to-be-implemented methods
    document the available events that are triggered during the conversion
    process.

    Extension classes should have a :py:attr:`_helptext` attribute. It's used
    to display a brief summary.

    :param manifest: Content manifest.
    :type manifest: innoconv.manifest.Manifest
    """

    _helptext = ""

    def __init__(self, manifest):
        """Initialize variables."""
        self._extensions = []
        self._manifest = manifest

    @classmethod
    def helptext(cls):
        """Return a brief summary of what the extension is doing."""
        return cls._helptext

    def extension_list(self, extensions):
        """
        Receive list of active extension instances.

        :param extensions: List of all active extension instances
        :type extensions: list
        """
        self._extensions = extensions

    def start(self, output_dir, source_dir):
        """
        Conversion is about to start.

        :param output_dir: Base output directory
        :type output_dir: str
        :param source_dir: Content source directory
        :type source_dir: str
        """

    def pre_conversion(self, language):
        """
        Conversion of a single language folder is about to start.

        :param language: Language that is currently being converted.
        :type language: str
        """

    def pre_process_file(self, path):
        """
        Conversion of a single file is about to start.

        :param path: Output path
        :type path: str
        """

    def post_process_file(
        self, ast, title, content_type, section_type=None, short_title=None
    ):
        """
        Conversion of a single file finished. The AST can be modified.

        :param ast: File content as parsed by pandoc.
        :type ast: List of content nodes
        :param title: Section title (localized)
        :type title: str
        :param content_type: Content type ('section' or 'custom')
        :type content_type: str
        :param section_type: Section type ('exercises', 'test' or None)
        :type section_type: str
        :param short_title: Section title short form (localized)
        :type section_type: str
        """

    def post_conversion(self, language):
        """
        Conversion of a single language folder finished.

        :param language: Language that is currently being converted.
        :type language: str
        """

    def finish(self):
        """Conversion finished."""
