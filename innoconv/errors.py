"""Exceptions are defined here."""


class ParseError(ValueError):
    """Raised when a mintmod command could not be parsed."""
    pass


class NoPrecedingHeader(ParseError):
    """Raised when a there's no preceding header for a MSectionStart."""
    pass
