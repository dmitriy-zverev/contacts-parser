import sys

from contacts_parser.parser.errors import PermanentParserError
from contacts_parser.parser.parser import Parser

if len(sys.argv) < 2:
    raise PermanentParserError("Must provide url")

parser = Parser(sys.argv[1])

parser.get_emails()
