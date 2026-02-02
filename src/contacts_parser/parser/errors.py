class ParserError(Exception):
    pass


class TransientParserError(ParserError):
    """Temporary error. Safe to retry"""

    pass


class PermanentParserError(ParserError):
    """Permanent error. Retrying won't help"""

    pass


class NoContentParserError(ParserError):
    """Not found. No need to retry"""

    pass


class MaxPagesParserError(ParserError):
    """Error for maximum number of pages"""

    pass
