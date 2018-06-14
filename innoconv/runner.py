"""Runner module"""


class InnoconvRunner():
    """innoConv runner.

    It walks over the course files and converts them to JSON.
    """

    def __init__(self, source, output_dir_base, languages, debug=False):
        self.source = source
        self.output_dir_base = output_dir_base
        self.languages = languages
        self.debug = debug

    def run(self):
        """Start the conversion."""
        pass
