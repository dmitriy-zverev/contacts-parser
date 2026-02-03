import re

from bs4 import BeautifulSoup


def _normalize_russian_phone_variants(raw_digits: str) -> set[str]:
    digits = re.sub(r"\D", "", raw_digits)

    if len(digits) == 11 and digits[0] in {"7", "8"}:
        core = digits[1:]
    elif len(digits) == 10 and digits[0] in {"9", "4", "8"}:
        core = digits
    else:
        return set()

    return {f"+7{core}", f"7{core}", f"8{core}"}


def _extract_russian_phones(text: str) -> set[str]:
    phone_pattern = re.compile(r"(?:\+7|7|8)?[\s\-()]*\d{3}[\s\-()]*\d{3}[\s\-]*\d{2}[\s\-]*\d{2}")
    phones: set[str] = set()

    for match in phone_pattern.findall(text):
        phones.update(_normalize_russian_phone_variants(match))

    return phones


def _is_valid_email(email: str) -> bool:
    invalid_suffixes = (
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".webp",
        ".svg",
        ".ico",
        ".bmp",
        ".tiff",
    )
    lowered = email.lower()

    if lowered.endswith(invalid_suffixes):
        return False

    return True


def grab_contacts(
    page: BeautifulSoup,
) -> dict[
    dict[str, list[str]],
    dict[str, list[str]],
]:
    email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")

    attribute_values: list[str] = []
    for element in page.select("[href], [src]"):
        href_value = element.get("href")
        src_value = element.get("src")
        if href_value:
            attribute_values.append(href_value)
        if src_value:
            attribute_values.append(src_value)

    emails = set(
        filter(
            None,
            [
                email_link.get("href").removeprefix("mailto:").split("?")[0].strip()
                for email_link in page.select("[href^='mailto:']")
            ],
        )
    )

    combined_text = " ".join([page.get_text(), *attribute_values])
    emails.update(filter(_is_valid_email, email_pattern.findall(combined_text)))

    phones: set[str] = set()
    for element in page.select("[href^='tel:'], [src^='tel:']"):
        value = element.get("href") or element.get("src")
        if value:
            phones.update(_normalize_russian_phone_variants(value.removeprefix("tel:").split("?")[0]))

    phones.update(_extract_russian_phones(combined_text))

    return {
        "emails": list(emails),
        "phones": list(phones),
    }
