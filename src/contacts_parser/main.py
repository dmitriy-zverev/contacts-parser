import logging
import sys

from contacts_parser.core.config import settings
from contacts_parser.parser.errors import PermanentParserError
from contacts_parser.parser.parser import Parser

logging.basicConfig(level=settings.log_level)

if len(sys.argv) < 2:
    raise PermanentParserError("Must provide URL")

url = sys.argv[1]

parser = Parser(url)
result = parser.run()

print(f"Base url: {result.base_url}")
print(f"Number of pages: {result.pages_parsed}")
print(f"Contacts: {{'url': '{result.url}', 'emails': {result.emails}, 'phones': {result.phones}}}")
