"""Base classes are defined here."""


class BaseLatexToken():

    """A LaTeX token.

    This can be either a command or an environment.
    """

    def __init__(self, doc=None):
        self._doc = doc

    @property
    def doc(self):
        """``doc`` property."""
        return self._doc

    @doc.setter
    def doc(self, value):
        self._doc = value
