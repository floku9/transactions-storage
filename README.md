# goods-reservation

## Description

API that is used to store transactions. Also has opportunity to get historical information about clients balance.

## Common installation steps

1. Clone the repository:

   ```bash
   git clone https://github.com/floku9/transactions-storage
   cd transactions-storage
   ```

2. Create .env file that is suitable for your case, or just copy .env-example and delete -example part

## Running with Docker Compose

### Prerequisites

- Docker
- Docker Compose

To run the project with Docker Compose, follow these additional steps:

1. Up the docker compose

    ```bash
    docker-compose up --build
    ```

After this step, the project will be available at <http://localhost:8000> (if you use default settings). Also will be up celery worker, redis and db instance.

## Running tests

### Prerequisites

- Python 3.12
- Poetry

To run the test without docker compose, you need to follow these steps:

1. Install poetry (if you don't have it):

    ```bash
    pip install poetry
    ```

2. Install dependencies:

    ```bash
    poetry install
    ```

3. Run the tests:

    3.1. To run tests without coverage use the following command:

    ```bash
    poetry run pytest tests
    ```

    3.2. To run tests with coverage use the following command:

    ```bash
    poetry run pytest --cov=backend tests
    ```

    3.3 If you want to run tests with coverage report in file, you need to run the following command:

    ```bash
    poetry run pytest --cov=backend --cov=celery_app --cov-report=html tests
    ```

    Then in your local folder will be created folder called `htmlcov` with coverage report.
