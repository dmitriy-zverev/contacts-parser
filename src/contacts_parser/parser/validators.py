from urllib.parse import urlparse, urlunparse

from contacts_parser.parser.errors import PermanentParserError


def validate_and_normalize_url(url: str) -> str:
    url = url.strip()

    p = urlparse(url)

    if p.scheme not in ("http", "https"):
        return PermanentParserError("URL должен начинаться с http:// или https://")

    if not p.netloc:
        return PermanentParserError("URL должен быть абсолютным и содержать домен типа https://example.com")

    normalized = urlunparse(
        (
            p.scheme,
            p.netloc.replace("www.", "", 1) if p.netloc.startswith("www.") else p.netloc,
            p.path or "/",
            p.params,
            p.query,
            "",
        )
    )

    return normalized


def parse_base_url(url: str) -> str:
    normilized_p = urlparse(validate_and_normalize_url(url))

    base_url = urlunparse(
        (
            normilized_p.scheme,
            normilized_p.netloc,
            "/",
            "",
            "",
            "",
        )
    )

    return base_url
