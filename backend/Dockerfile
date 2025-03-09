    FROM python:3.12-slim

    WORKDIR /transaction-storage-backend

    RUN apt-get update && apt-get install -y \
        libpq-dev gcc && \
        rm -rf /var/lib/apt/lists/*


    RUN pip install --no-cache-dir poetry

    COPY pyproject.toml poetry.lock ./

    RUN poetry install --no-root

    COPY .env settings.py ./
    COPY backend ./backend
    COPY db ./db
    COPY utils ./utils


    EXPOSE 8000

    CMD ["poetry", "run", "uvicorn", "backend.application.app:app", "--host", "0.0.0.0", "--port", "8000"]