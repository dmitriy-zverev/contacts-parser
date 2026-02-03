from bs4 import BeautifulSoup

from contacts_parser.parser.utils import grab_contacts


def test_grab_contacts_extracts_emails_and_phones() -> None:
    html = """
    <html>
        <body>
            <a href="mailto:info@example.com">Email</a>
            <a href="tel:+7 (999) 123-45-67">Phone</a>
            <img src="tel:89991234567" />
            <p>Support: support@example.com, Sales: 7 999 123-45-67</p>
            <img src="photo@1x.png" />
        </body>
    </html>
    """
    soup = BeautifulSoup(html, "html.parser")

    contacts = grab_contacts(soup)

    assert set(contacts["emails"]) == {"info@example.com", "support@example.com"}
    assert set(contacts["phones"]) == {
        "+79991234567",
        "79991234567",
        "89991234567",
    }
