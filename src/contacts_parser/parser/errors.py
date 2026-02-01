class ParserError(Exception):
    pass


class TransientParserError(ParserError):
    """Temporary error. Safe to retry"""

    pass


class PermanentParserError(ParserError):
    """Permanent error. Retrying won't help"""

    pass
