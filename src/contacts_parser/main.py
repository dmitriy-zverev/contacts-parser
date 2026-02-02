import sys

from contacts_parser.parser.errors import PermanentParserError
from contacts_parser.parser.parser import Parser

if len(sys.argv) < 2:
    raise PermanentParserError("Must provide URL")

url = sys.argv[1]

parser = Parser(url)
parser.run()

print(f"Base url: {parser.get_base_url()}")
print(f"Number of pages: {len(parser.get_pages())}")
print(f"Contacts: {parser.get_contacts()}")
