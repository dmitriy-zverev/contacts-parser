from bs4 import BeautifulSoup

from contacts_parser.parser.parser import Parser


def test_find_all_links_filters_and_normalizes_links() -> None:
    parser = Parser("https://example.com/start")
    html = """
    <html>
        <body>
            <a href="https://example.com/about">About</a>
            <a href="https://example.com/contact?ref=nav">Contact</a>
            <a href="https://other.com/">External</a>
            <img src="https://example.com/static/logo.png" />
        </body>
    </html>
    """
    parser._pages[parser._init_url] = BeautifulSoup(html, "html.parser")

    links = parser.find_all_links(parser._init_url)

    assert set(links) == {
        "https://example.com/about",
        "https://example.com/contact?ref=nav",
    }
