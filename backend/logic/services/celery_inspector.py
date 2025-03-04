from celery import Celery
from celery.app.control import Inspect
from utils.logging import logger


class CeleryInspectorService:
    def __init__(self, celery_client: Celery):
        self._celery_client = celery_client

    def not_finished_tasks_count(self) -> int:
        """
        Calculate the total number of tasks that are not yet finished in the Celery system.

        This function inspects the current state of the Celery system to determine the number
        of active, reserved, and scheduled tasks, and logs this information.

        Returns:
            int: The total count of active, reserved, and scheduled tasks.
        """
        inspector = Inspect(self._celery_client)
        active_tasks = inspector.active() or {}
        reserved_tasks = inspector.reserved() or {}
        scheduled_tasks = inspector.scheduled() or {}

        active_count = sum(len(tasks) for tasks in active_tasks.values())
        reserved_count = sum(len(tasks) for tasks in reserved_tasks.values())
        scheduled_count = sum(len(tasks) for tasks in scheduled_tasks.values())

        logger.info(
            f"At current moment celery has {active_count} active tasks, "
            f"{reserved_count} reserved tasks and {scheduled_count} scheduled tasks"
        )
        return active_count + reserved_count + scheduled_count
