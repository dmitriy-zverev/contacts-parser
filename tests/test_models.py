from datetime import datetime, timedelta

from contacts_parser.parser.models import ParserResult


def test_parser_result_duration_seconds() -> None:
    started = datetime.utcnow()
    finished = started + timedelta(seconds=2)
    result = ParserResult(
        url="https://example.com",
        base_url="https://example.com/",
        pages_parsed=1,
        emails=["info@example.com"],
        phones=["+79991234567"],
        started_at=started,
        finished_at=finished,
    )

    assert result.duration_seconds == 2.0
