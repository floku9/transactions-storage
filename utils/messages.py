from enum import Enum


class ErrorMessages(str, Enum):
    CELERY_IS_BUSY = "Celery still processing tasks, wait for celery to finish."
