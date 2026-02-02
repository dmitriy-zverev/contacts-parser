from __future__ import annotations

from time import sleep

from bs4 import BeautifulSoup

from contacts_parser.core.config import settings
from contacts_parser.infra.client import request_data
from contacts_parser.infra.http import get_session
from contacts_parser.parser.errors import (
    MaxPagesParserError,
    NoContentParserError,
    PermanentParserError,
    TransientParserError,
)
from contacts_parser.parser.utils import grab_contacts
from contacts_parser.parser.validators import parse_base_url, validate_and_normalize_url


class Parser:
    def __init__(self, url: str) -> None:
        self._session = get_session()
        self._timeout = settings.http_timeout_seconds
        self._pages = dict()
        self._emails = set()
        self._phones = set()
        self._base_url = parse_base_url(url)
        self._init_url = validate_and_normalize_url(url)

    def run(self) -> None:
        print(f"""
        Starting url: {self._init_url}
        Base url: {self._base_url}
        Max pages deep: {settings.max_pages_deep}
        Max retries: {settings.http_max_retries}
        Timeout: {settings.http_timeout_seconds}s
        Backoff: {settings.http_backoff_seconds}s
        """)

        # Parse init url
        self.parse_page(self._init_url)

        # Main loop: select related links and parse them
        self.find_related_pages(self._init_url)

    def parse_page(self, url: str) -> None:
        if len(self._pages) == settings.max_pages_deep:
            raise MaxPagesParserError("You've reached limit on number of pages")

        print(f"Parsing {url}...")
        resp = None
        for _ in range(settings.http_max_retries):
            try:
                resp = request_data(self._session, url, self._timeout)
                break
            except NoContentParserError:
                break
            except TransientParserError as e:
                print(f"Transient parser error: {str(e)}. Retrying in {settings.http_backoff_seconds}s")
                sleep(settings.http_backoff_seconds)
                continue
            except PermanentParserError as e:
                raise e

        try:
            if resp:
                page = BeautifulSoup(resp.content, settings.parser_type)
                self._pages[url] = page
                contacts = grab_contacts(page)
                self._emails.update(contacts["emails"])
                self._phones.update(contacts["phones"])

        except Exception as e:
            raise PermanentParserError(str(e)) from e

    def find_related_pages(self, starting_url: str) -> None:
        url_list = self.find_all_links(starting_url)

        for url in url_list:
            if url not in self._pages.keys():
                try:
                    self.parse_page(url)
                except MaxPagesParserError:
                    break
                except PermanentParserError as e:
                    raise e
                self.find_related_pages(url)

    def find_all_links(self, url: str) -> list[str]:
        try:
            page_links = self.get_page(url).select("[href], [src]")
        except KeyError:
            print("No content on the page")
            return []

        url_list = set()
        for page_link in page_links:
            url = page_link.get("href")
            if url and url.startswith(self._base_url):
                url_list.add(validate_and_normalize_url(url))

        return list(url_list)

    def get_page(self, url: str) -> BeautifulSoup | None:
        return self._pages[validate_and_normalize_url(url)]

    def get_pages(self) -> dict[str, BeautifulSoup]:
        return self._pages

    def get_pages_len(self) -> int:
        return len(self._pages)

    def get_base_url(self) -> str:
        return self._base_url

    def get_emails(self) -> list[str]:
        return list(self._emails)

    def get_phones(self) -> list[str]:
        return list(self._phones)

    def get_contacts(
        self,
    ) -> dict[
        dict[str, str],
        dict[str, set[str]],
        dict[str, set[str]],
    ]:
        return {
            "url": self._init_url,
            "emails": self.get_emails(),
            "phones": self.get_phones(),
        }
