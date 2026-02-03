.PHONY: build run run-detached lint test test-cov run-local run-api

build:
	docker build -t contacts-parser .

run:
	docker run --rm contacts-parser https://example.com

run-detached:
	docker run -d --rm -p 8000:8000 --name contacts-parser contacts-parser

run-local:
	python -m contacts_parser.main https://example.com

run-api:
	uvicorn contacts_parser.api.main:app --host 127.0.0.1 --port 8000

lint:
	pre-commit run --all-files

test:
	pytest tests

test-cov:
	pytest tests --cov=. --cov-config=tests/.coveragerc --cov-report term