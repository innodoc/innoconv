"""The AbstractExtension is not meant to be instantiated directly."""


class AbstractExtension():
    """Abstract class for extensions.

    The class all extensions inherit from. The to-be-implemented methods
    document the available events. Sub-classes should implement all of these
    methods even if they don't need to add functionality to each.
    """

    _helptext = ''

    def __init__(self):
        self.events = []

    @classmethod
    def helptext(cls):
        """Return a brief summary of what the extension is doing."""
        return cls._helptext

    def init(self, languages, output_dir_base, source_dir):
        """Conversion is about to start.

        :param languages: List of languages that are being converted.
        :type languages: List of str
        :param output_dir_base: Base output directory
        :type output_dir_base: str
        :param source_dir: Content source directory
        :type source_dir: str
        """
        raise NotImplementedError()

    def pre_conversion(self, language):
        """Conversion of a single language folder is about to start.

        :param languages: List of languages that are being converted.
        :type languages: List of str
        """
        raise NotImplementedError()

    def pre_process_file(self, rel_path, fullpath):
        """Conversion of a single file is about to start.

        :param rel_path: File path relative to project source directory
        :type rel_path: str
        :param fullpath: Absolute file path
        :type fullpath: str
        """
        raise NotImplementedError()

    def post_process_file(self, ast):
        """Conversion of a single file finished. The AST can be modified.

        :param ast: File content as parsed by pandoc.
        :type ast: List of content nodes
        """
        raise NotImplementedError()

    def post_conversion(self, language):
        """Conversion of a single language folder finished.

        :param languages: List of languages that are being converted.
        :type languages: List of str
        """
        raise NotImplementedError()

    def finish(self, language):
        """Conversion finished."""
        raise NotImplementedError()
