FROM python:3.12-slim

WORKDIR /transaction-storage-migrations

RUN apt-get update && apt-get install -y \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./ 

RUN poetry install --no-root

COPY .env settings.py alembic.ini ./
COPY alembic ./alembic
COPY db ./db

CMD ["poetry", "run", "alembic", "upgrade", "head"]
