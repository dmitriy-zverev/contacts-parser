from contacts_parser.core.config import settings
from contacts_parser.infra.http import get_session


def test_get_session_sets_user_agent() -> None:
    session = get_session()

    assert session.headers["User-Agent"] == settings.http_user_agent
