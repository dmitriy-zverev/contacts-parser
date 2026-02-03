FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml /app/pyproject.toml
COPY src /app/src
COPY .env.example /app/.env.example

RUN pip install --no-cache-dir -e .

RUN useradd -m appuser
USER appuser

EXPOSE 8000

ENTRYPOINT ["uvicorn", "contacts_parser.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
