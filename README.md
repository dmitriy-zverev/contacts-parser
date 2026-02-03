# Contacts Parser

A production-grade contacts parser that crawls a site, extracts emails and Russian phone numbers, and returns structured results. The project ships both a CLI and a FastAPI service for programmatic use.

## Features
- Threaded crawler with bounded worker pool
- Email extraction from text and `mailto:` links
- Russian phone number extraction with +7/7/8 normalization
- Configurable HTTP timeouts, retries, backoff, user-agent, and request delay
- Structured results (`ParserResult`) with timing metadata
- Logging instead of raw `print()` output

## Architecture
- **core**: configuration and settings
- **infra**: HTTP sessions, request logic, retry/backoff handling
- **parser**: crawler, URL normalization, extraction utilities, result model
- **api**: FastAPI app exposing `/parse`

## Requirements
- Python 3.11+

## Install
```bash
pip install -e .
```

### Production install (pip)
```bash
pip install -r requirements.txt
```

## CLI usage
```bash
python -m contacts_parser.main https://example.com
```

## API usage
Start the API server:
```bash
uvicorn contacts_parser.api.main:app --host 127.0.0.1 --port 8000
```

Call the endpoint:
```bash
curl -X POST http://127.0.0.1:8000/parse \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

Response:
```json
{
  "url": "https://example.com",
  "emails": ["info@example.com"],
  "phones": ["+79991234567"]
}
```

## Docker
Build and run the API server:
```bash
make build
make run-detached
```

Stop the container:
```bash
docker stop contacts-parser
```

## Result format
The parser returns a `ParserResult` object with:
- `url` and `base_url`
- `pages_parsed`
- `emails` and `phones`
- `started_at`, `finished_at`, and `duration_seconds`

## Logging
Logging is enabled via `LOG_LEVEL` and uses the standard library `logging` module:
```bash
LOG_LEVEL=DEBUG python -m contacts_parser.main https://example.com
```

## Configuration (.env)
All settings are configurable via environment variables. See `.env.example` for defaults.

### Common
| Variable | Description | Default |
| --- | --- | --- |
| `APP_NAME` | App name | `contacts-parser` |
| `ENV` | Environment (`dev`, `test`, `prod`) | `dev` |
| `LOG_LEVEL` | Logging level | `INFO` |

### HTTP
| Variable | Description | Default |
| --- | --- | --- |
| `HTTP_TIMEOUT_SECONDS` | Request timeout | `5.0` |
| `HTTP_MAX_RETRIES` | Max retry attempts | `3` |
| `HTTP_BACKOFF_SECONDS` | Retry backoff seconds | `0.2` |
| `HTTP_USER_AGENT` | User-Agent header | `contacts-parser/0.1` |
| `HTTP_MIN_DELAY_SECONDS` | Delay between requests | `0.0` |
| `POOL_CONNECTIONS` | Requests pool connections | `10` |
| `POOL_MAXSIZE` | Requests pool max size | `10` |
| `LRU_MAXSIZE` | Session cache size | `1` |

### Parser
| Variable | Description | Default |
| --- | --- | --- |
| `PARSER_TYPE` | BeautifulSoup parser | `html.parser` |
| `MAX_PAGES_DEEP` | Max pages to parse | `1000` |
| `CRAWLER_MAX_WORKERS` | Thread pool size | `8` |

## Examples
### Custom user-agent and throttling
```bash
HTTP_USER_AGENT="my-bot/1.0" \
HTTP_MIN_DELAY_SECONDS=0.3 \
python -m contacts_parser.main https://example.com
```

### Limit crawl depth and workers
```bash
MAX_PAGES_DEEP=100 \
CRAWLER_MAX_WORKERS=4 \
python -m contacts_parser.main https://example.com
```

### Local API request
```bash
curl -X POST http://127.0.0.1:8000/parse \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```