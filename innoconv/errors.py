"""Exceptions are defined here."""


class ParseError(ValueError):
    """Raised when a mintmod command cannot be parsed."""
    pass


class NoPrecedingHeader(ParseError):
    """Raised when a there's no preceding header for a MSectionStart."""
    pass


class PandocError(ParseError):
    """Raised when a Pandoc process fails."""
    pass
