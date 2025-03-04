# Тест метода not_finished_tasks_count
from mock import Mock, patch

from backend.logic.services.celery_inspector import CeleryInspectorService


def test_not_finished_tasks_count(test_celery_inspector_service: CeleryInspectorService, mocker):
    mock_inspector = Mock()
    with patch("backend.logic.services.celery_inspector.Inspect", return_value=mock_inspector):

        mock_inspector.active.return_value = {"worker1": ["task1", "task2"]}
        mock_inspector.reserved.return_value = {"worker1": ["task3"]}
        mock_inspector.scheduled.return_value = {"worker1": []}

        result = test_celery_inspector_service.not_finished_tasks_count()

    assert result == 3


def test_not_inspector_empty_tasks(test_celery_inspector_service: CeleryInspectorService, mocker):
    mock_inspector = Mock()
    with patch("backend.logic.services.celery_inspector.Inspect", return_value=mock_inspector):

        mock_inspector.active.return_value = {"worker1": []}
        mock_inspector.reserved.return_value = {"worker1": []}
        mock_inspector.scheduled.return_value = {"worker1": []}

        result = test_celery_inspector_service.not_finished_tasks_count()

    assert result == 0
