from urllib.parse import urlparse, urlunparse

from contacts_parser.parser.errors import PermanentParserError


def validate_and_normalized_url(url: str) -> str:
    url = url.strip()

    p = urlparse(url)

    if p.scheme not in ("http", "https"):
        return PermanentParserError("URL должен начинаться с http:// или https://")

    if not p.netloc:
        return PermanentParserError("URL должен быть абсолютным и содержать домен типа https://example.com")

    normalized = urlunparse(
        (
            p.scheme,
            p.netloc,
            p.path or "/",
            p.params,
            p.query,
            "",
        )
    )

    return normalized
