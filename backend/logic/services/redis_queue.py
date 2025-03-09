# redis_queue_service.py
import json
from typing import Optional

import redis

from backend.logic.dto import TaskInfoDTO
from utils.logging import logger


class RedisQueueService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def get_not_finished_tasks(self, queue_name: str) -> int:
        """
        Returns the number of unfinished tasks in the specified queue

        Args:
            queue_name: Name of the queue (e.g., 'celery')
        Returns:
            int: Number of unfinished tasks
        """
        logger.debug(f"Fetching unfinished tasks from queue {queue_name}")
        tasks = self.redis.lrange(queue_name, 0, -1)

        logger.debug(f"Found {len(tasks)} unfinished tasks in {queue_name}")
        return len(tasks)

    def get_task_status(self, task_id: str) -> Optional[TaskInfoDTO]:
        """
        Retrieves the status of a task by its ID

        Args:
            task_id: ID of the Celery task
        Returns:
            TaskStatus: Model with task information or None if task is not found
        """
        logger.debug(f"Fetching status for task {task_id}")
        task_key = f"celery-task-meta-{task_id}"
        result = self.redis.get(task_key)

        if result is None:
            logger.info(f"Task {task_id} not found")
            return None

        result_dict = json.loads(result)
        status = TaskInfoDTO(**result_dict)
        logger.debug(f"Task {task_id} status: {status.status}")
        return status
