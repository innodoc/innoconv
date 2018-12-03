"""The AbstractExtension is not meant to be instantiated directly."""


class AbstractExtension():
    """Abstract class for extensions.

    The class all extensions inherit from. The to-be-implemented methods
    document the available events that are triggered during the conversion
    process.

    Extension classes should have a ``_helptext`` attribute. It is shown in the
    CLI as a brief summary what the extension accomplishes.
    """

    _helptext = ''

    def __init__(self, manifest):
        self._manifest = manifest

    @classmethod
    def helptext(cls):
        """Return a brief summary of what the extension is doing."""
        return cls._helptext

    def start(self, output_dir, source_dir):
        """Conversion is about to start.

        :param output_dir: Base output directory
        :type output_dir: str
        :param source_dir: Content source directory
        :type source_dir: str
        """
        raise NotImplementedError()

    def pre_conversion(self, language):
        """Conversion of a single language folder is about to start.

        :param language: Language that is currently being converted.
        :type language: str
        """
        raise NotImplementedError()

    def pre_process_file(self, path):
        """Conversion of a single file is about to start.

        :param path: Output path
        :type path: str
        """
        raise NotImplementedError()

    def post_process_file(self, ast, title):
        """Conversion of a single file finished. The AST can be modified.

        :param ast: File content as parsed by pandoc.
        :type ast: List of content nodes
        :param title: Section title (localized)
        :type title: str
        """
        raise NotImplementedError()

    def post_conversion(self, language):
        """Conversion of a single language folder finished.

        :param language: Language that is currently being converted.
        :type language: str
        """
        raise NotImplementedError()

    def finish(self):
        """Conversion finished."""
        raise NotImplementedError()