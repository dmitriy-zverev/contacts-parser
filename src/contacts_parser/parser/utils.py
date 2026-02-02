import re

from bs4 import BeautifulSoup


def grab_contacts(
    page: BeautifulSoup,
) -> dict[
    dict[str, list[str]],
    dict[str, list[str]],
]:
    emails = set(
        filter(
            None,
            [
                email_link.get("href").strip("mailto:").split("?")[0].strip()
                for email_link in page.select("[href^='mailto:']")
            ],
        )
    )

    text = page.get_text()
    email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
    emails.update(email_pattern.findall(text))

    phones = set(
        filter(
            None,
            [
                phone_link.get("href")
                .strip("tel:")
                .replace("+", "")
                .strip()
                .replace("-", "")
                .replace(" ", "")
                .replace("(", "")
                .replace(")", "")
                for phone_link in page.select("[href^='tel:']")
            ],
        )
    )

    return {
        "emails": list(emails),
        "phones": list(phones),
    }
