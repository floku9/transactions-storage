from datetime import datetime

from backend.logic.dto import TaskInfoDTO


def test_get_task_status_success(test_client, test_redis_queue_service):
    task_id = "test-task-123"
    task_info = TaskInfoDTO(
        task_id=task_id,
        status="SUCCESS",
        result="Task completed",
        date_done=datetime.now().isoformat(),
    )
    test_redis_queue_service.redis.set(
        f"celery-task-meta-{task_id}", TaskInfoDTO.model_dump_json(task_info)
    )
    response = test_client.get(f"/celery/task_status/{task_id}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "SUCCESS"
    assert response_data["result"] == "Task completed"
    assert response_data["date_done"] == task_info.date_done
    assert response_data["traceback"] is None


def test_get_task_status_not_found(test_client, test_redis_queue_service):
    task_id = "non-existent-task-456"
    response = test_client.get(f"/celery/task_status/{task_id}")
    assert response.status_code == 404
