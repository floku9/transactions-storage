# test_redis_queue_service.py
import json

from backend.logic.dto import TaskInfoDTO


def test_get_not_finished_tasks_empty_queue(test_redis_queue_service):
    assert test_redis_queue_service.get_not_finished_tasks("test_queue") == 0


def test_get_not_finished_tasks(test_redis_queue_service, test_redis_client):
    queue_name = "test_queue"

    task1 = {"task_id": "task1", "body": "some_work"}
    test_redis_client.lpush(queue_name, json.dumps(task1))

    assert test_redis_queue_service.get_not_finished_tasks(queue_name) == 1


def test_get_task_status_not_found(test_redis_queue_service):
    result = test_redis_queue_service.get_task_status("non_existent_task")
    assert result is None


def test_get_task_status_full_info(test_redis_queue_service, test_redis_client):
    task_id = "test_task_123"
    task_key = f"celery-task-meta-{task_id}"
    task_data = {
        "status": "SUCCESS",
        "result": "done",
        "traceback": None,
        "date_done": "2025-03-08T12:00:00",
    }

    test_redis_client.set(task_key, json.dumps(task_data))

    status = test_redis_queue_service.get_task_status(task_id)
    assert isinstance(status, TaskInfoDTO)
    assert status.status == "SUCCESS"
    assert status.result == "done"
    assert status.traceback is None
    assert status.date_done == "2025-03-08T12:00:00"
