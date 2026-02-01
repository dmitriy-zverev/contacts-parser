from __future__ import annotations

from requests.exceptions import (
    ConnectionError,
    HTTPError,
    RequestException,
    SSLError,
    Timeout,
)

from contacts_parser.core.config import settings
from contacts_parser.infra.http import get_session
from contacts_parser.parser.errors import PermanentParserError, TransientParserError
from contacts_parser.parser.validators import validate_and_normalized_url


class Parser:
    def __init__(self, url: str) -> None:
        self._session = get_session()
        self._timeout = settings.http_timeout_seconds
        self._base_url = validate_and_normalized_url(url)

    def get_emails(self) -> list[str]:
        try:
            resp = self._session.get(self._base_url, timeout=self._timeout)
            resp.raise_for_status()
        except (Timeout, ConnectionError, SSLError) as e:
            raise TransientParserError(str(e)) from e
        except HTTPError as e:
            status = e.response.status_code if e.response is not None else None

            if status in (429, 500, 502, 503, 504):
                raise TransientParserError(f"HTTP {status}") from e

            raise PermanentParserError(f"HTTP {status}") from e
        except RequestException as e:
            raise TransientParserError(str(e)) from e

        try:
            idx = resp.text.find("mailto:")
            idx_2 = resp.text[idx:].find('"')
            print(resp.text[idx : idx + idx_2])
        except ValueError as e:
            raise TransientParserError(str(e)) from e
