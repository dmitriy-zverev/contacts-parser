from time import sleep

import requests
from requests.exceptions import (
    ConnectionError,
    HTTPError,
    RequestException,
    SSLError,
    Timeout,
)

from contacts_parser.core.config import settings
from contacts_parser.parser.errors import NoContentParserError, PermanentParserError, TransientParserError


def request_data(session: requests.Session, url: str, timeout: int) -> requests.Response:
    if settings.http_min_delay_seconds > 0:
        sleep(settings.http_min_delay_seconds)
    try:
        resp = session.get(url, timeout=timeout)
        resp.raise_for_status()
    except (Timeout, ConnectionError, SSLError) as e:
        raise TransientParserError(str(e)) from e
    except HTTPError as e:
        status = e.response.status_code if e.response is not None else None

        if status in (403, 404):
            raise NoContentParserError(f"HTTP {status}") from e

        if status in (429, 500, 502, 503, 504):
            raise TransientParserError(f"HTTP {status}") from e

        raise PermanentParserError(f"HTTP {status}") from e
    except RequestException as e:
        raise TransientParserError(str(e)) from e

    return resp
