from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

from contacts_parser.parser.errors import ParserError, PermanentParserError
from contacts_parser.parser.parser import Parser


class ParseRequest(BaseModel):
    url: HttpUrl


class ParseResponse(BaseModel):
    url: str
    emails: list[str]
    phones: list[str]


app = FastAPI(title="contacts-parser")


@app.post("/parse", response_model=ParseResponse)
def parse_contacts(request: ParseRequest) -> ParseResponse:
    try:
        result = Parser(str(request.url)).run()
        return ParseResponse(url=result.url, emails=result.emails, phones=result.phones)
    except PermanentParserError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ParserError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
