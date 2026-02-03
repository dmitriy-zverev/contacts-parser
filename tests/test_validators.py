import pytest

from contacts_parser.parser.errors import PermanentParserError
from contacts_parser.parser.validators import parse_base_url, validate_and_normalize_url


def test_validate_and_normalize_url_normalizes_www_and_path() -> None:
    url = "https://www.example.com/contact"

    assert validate_and_normalize_url(url) == "https://example.com/contact"


@pytest.mark.parametrize("url", ["example.com", "ftp://example.com", "//example.com"])
def test_validate_and_normalize_url_requires_scheme(url: str) -> None:
    with pytest.raises(PermanentParserError):
        validate_and_normalize_url(url)


@pytest.mark.parametrize("url", ["http://", "https://"])
def test_validate_and_normalize_url_requires_netloc(url: str) -> None:
    with pytest.raises(PermanentParserError):
        validate_and_normalize_url(url)


def test_parse_base_url_strips_path() -> None:
    assert parse_base_url("https://example.com/sub/page") == "https://example.com/"
