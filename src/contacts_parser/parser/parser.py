from __future__ import annotations

import logging
from collections import deque
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from datetime import datetime
from threading import Lock
from time import sleep

from bs4 import BeautifulSoup

from contacts_parser.core.config import settings
from contacts_parser.infra.client import request_data
from contacts_parser.infra.http import get_thread_session
from contacts_parser.parser.errors import (
    MaxPagesParserError,
    NoContentParserError,
    PermanentParserError,
    TransientParserError,
)
from contacts_parser.parser.models import ParserResult
from contacts_parser.parser.utils import grab_contacts
from contacts_parser.parser.validators import parse_base_url, validate_and_normalize_url


class Parser:
    def __init__(self, url: str) -> None:
        self._timeout = settings.http_timeout_seconds
        self._pages = dict()
        self._emails = set()
        self._phones = set()
        self._state_lock = Lock()
        self._base_url = parse_base_url(url)
        self._init_url = validate_and_normalize_url(url)
        self._logger = logging.getLogger(__name__)

    def run(self) -> ParserResult:
        started_at = datetime.utcnow()
        self._logger.info(
            "Starting parser",
            extra={
                "url": self._init_url,
                "base_url": self._base_url,
                "max_pages": settings.max_pages_deep,
                "max_retries": settings.http_max_retries,
                "timeout": settings.http_timeout_seconds,
                "backoff": settings.http_backoff_seconds,
            },
        )

        # Main loop: select related links and parse them
        self.find_related_pages(self._init_url)

        finished_at = datetime.utcnow()
        result = ParserResult(
            url=self._init_url,
            base_url=self._base_url,
            pages_parsed=self.get_pages_len(),
            emails=self.get_emails(),
            phones=self.get_phones(),
            started_at=started_at,
            finished_at=finished_at,
        )
        self._logger.info(
            "Parser finished",
            extra={
                "url": result.url,
                "pages_parsed": result.pages_parsed,
                "emails_found": len(result.emails),
                "phones_found": len(result.phones),
                "duration_seconds": result.duration_seconds,
            },
        )
        return result

    def parse_page(self, url: str) -> None:
        with self._state_lock:
            if len(self._pages) >= settings.max_pages_deep:
                raise MaxPagesParserError("You've reached limit on number of pages")

        self._logger.debug("Parsing page", extra={"url": url})
        resp = None
        for _ in range(settings.http_max_retries):
            try:
                resp = request_data(get_thread_session(), url, self._timeout)
                break
            except NoContentParserError:
                break
            except TransientParserError as e:
                self._logger.warning(
                    "Transient parser error; retrying",
                    extra={"error": str(e), "backoff": settings.http_backoff_seconds, "url": url},
                )
                sleep(settings.http_backoff_seconds)
                continue
            except PermanentParserError as e:
                raise e

        try:
            if resp:
                page = BeautifulSoup(resp.content, settings.parser_type)
                contacts = grab_contacts(page)
                with self._state_lock:
                    self._pages[url] = page
                    self._emails.update(contacts["emails"])
                    self._phones.update(contacts["phones"])

        except Exception as e:
            raise PermanentParserError(str(e)) from e

    def find_related_pages(self, starting_url: str) -> None:
        queue = deque([starting_url])
        visited = {starting_url}

        with ThreadPoolExecutor(max_workers=settings.crawler_max_workers) as executor:
            futures: dict = {}

            while queue or futures:
                while queue and len(futures) < settings.crawler_max_workers:
                    url = queue.popleft()
                    futures[executor.submit(self.parse_page, url)] = url

                if not futures:
                    continue

                done, _ = wait(futures, return_when=FIRST_COMPLETED)

                for future in done:
                    url = futures.pop(future)
                    try:
                        future.result()
                    except MaxPagesParserError:
                        return
                    except PermanentParserError as e:
                        raise e

                    for next_url in self.find_all_links(url):
                        if next_url in visited:
                            continue
                        visited.add(next_url)
                        queue.append(next_url)

    def find_all_links(self, url: str) -> list[str]:
        try:
            page_links = self.get_page(url).select("[href], [src]")
        except KeyError:
            self._logger.debug("No content on the page", extra={"url": url})
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

    def get_contacts(self) -> dict[str, list[str] | str]:
        return {
            "url": self._init_url,
            "emails": self.get_emails(),
            "phones": self.get_phones(),
        }
