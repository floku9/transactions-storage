FROM python:3.12-slim

WORKDIR /transaction-storage-celery

RUN apt-get update && apt-get install -y \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./ 

RUN poetry install --no-root

COPY .env settings.py ./
COPY celery_app ./celery_app
COPY db ./db
COPY utils ./utils

CMD ["poetry", "run", "celery", "-A", "celery_app.tasks", "worker", "--loglevel=info"]
