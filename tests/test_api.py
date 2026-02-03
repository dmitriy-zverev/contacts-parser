from fastapi.testclient import TestClient

from contacts_parser.api.main import app


def test_parse_contacts_invalid_url() -> None:
    client = TestClient(app)

    response = client.post("/parse", json={"url": "not-a-url"})

    assert response.status_code == 422
