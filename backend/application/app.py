from typing import Callable

import uvicorn
from fastapi import FastAPI, Request, Response

from backend.application.routes.transactions import transactions_router
from settings import backend_settings
from utils.logging import logger

app = FastAPI(
    title="Transactions Storage API",
    version="0.1.0",
    description="API for storing transactions",
)

app.include_router(transactions_router)


@app.middleware("http")
async def logging_middleware(request: Request, call_next: Callable) -> Response:
    """
    Logs the incoming request and outgoing response for the current HTTP request.

    This middleware function is responsible for logging the details of the incoming HTTP request
    and the outgoing HTTP response. It logs the request method, URL,
    and the client's IP address and port. After the request is processed, it also logs the
    response status code, request method, and URL.

    """
    log_message = (
        f"Request: {request.method} {request.url} - "
        f"Client: {request.client.host}:{request.client.port}"  # type: ignore
    )

    logger.info(log_message)
    response = await call_next(request)

    logger.info(
        f"Response: Status {response.status_code} - Method: {request.method} - URL: {request.url}"
    )

    return response


if __name__ == "__main__":
    uvicorn.run(
        "backend.application.app:app",
        host=backend_settings.BACKEND_HOST,
        port=backend_settings.BACKEND_PORT,
        reload=True,
    )
