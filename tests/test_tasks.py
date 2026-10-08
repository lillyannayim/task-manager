import copy

import pytest
from services.tasks import TASKS, process_order, get_task, create_task, get_tasks_for_user, update_task
from utils.errors import NotFoundError, ValidationError

@pytest.fixture(autouse=True)
def restore_tasks():
    saved = copy.deepcopy(TASKS)
    yield
    TASKS.clear()
    TASKS.update(saved)

def test_process_order_valid():
    result = process_order(1)
    assert result["done"] is True

def test_process_order_invalid():
    with pytest.raises(Exception):
        process_order(999)

def test_get_task_valid():
    result = get_task(2)
    assert result["title"] == "Write report"

def test_get_task_invalid():
    with pytest.raises(Exception):
        get_task(999)

def test_get_task_not_found_error():
    with pytest.raises(NotFoundError, match="Task not found"):
        get_task(999)

def test_create_task_valid():
    result = create_task("Walk dog", 1)
    assert result["title"] == "Walk dog"
    assert result["done"] is False
    assert result["user_id"] == 1
    assert get_task(result["id"]) == result

def test_create_task_empty_title():
    with pytest.raises(ValidationError, match="Invalid title: cannot be empty"):
        create_task("   ", 1)

def test_get_tasks_for_user_valid():
    result = get_tasks_for_user(1)
    assert {1, 2} <= {task["id"] for task in result}
    assert all(task["user_id"] == 1 for task in result)

def test_get_tasks_for_user_not_found_error():
    with pytest.raises(NotFoundError, match="User not found"):
        get_tasks_for_user(999)

def test_seed_tasks_have_default_priority():
    assert all(get_task(task_id)["priority"] == 3 for task_id in (1, 2, 3))

def test_create_task_default_priority():
    assert create_task("Read book", 1)["priority"] == 3

def test_create_task_with_priority():
    result = create_task("Pay rent", 1, priority=5)
    assert result["priority"] == 5
    assert get_task(result["id"])["priority"] == 5

@pytest.mark.parametrize("priority", [0, 6, "3", 2.5, True])
def test_create_task_invalid_priority(priority):
    with pytest.raises(ValidationError, match="Invalid priority"):
        create_task("Bad priority", 1, priority=priority)

def test_update_task_priority():
    assert update_task(2, priority=1)["priority"] == 1

def test_update_task_title():
    result = update_task(2, title="New title")
    assert result["title"] == "New title"
    assert result["priority"] == 3

def test_update_task_invalid_priority():
    with pytest.raises(ValidationError, match="Invalid priority"):
        update_task(2, title="Changed", priority=9)
    assert get_task(2)["title"] == "Write report"
    assert get_task(2)["priority"] == 3

def test_update_task_not_found_error():
    with pytest.raises(NotFoundError, match="Task not found"):
        update_task(999, priority=2)
