from services.users import get_user
from utils.errors import NotFoundError, ValidationError

TASKS: dict[int, dict] = {
    1: {"id": 1, "title": "Buy groceries",  "done": False, "user_id": 1, "priority": 3},
    2: {"id": 2, "title": "Write report",   "done": False, "user_id": 1, "priority": 3},
    3: {"id": 3, "title": "Call dentist",   "done": True,  "user_id": 2, "priority": 3},
}

def _validate_priority(priority: int) -> None:
    """Check that a priority is an integer between 1 and 5.

    Args:
        priority: The priority value to check.

    Returns:
        None.

    Raises:
        ValidationError: If priority is not an int (bools excluded) between 1 and 5.
    """
    if not isinstance(priority, int) or isinstance(priority, bool) or not 1 <= priority <= 5:
        raise ValidationError("priority", "must be an integer between 1 and 5")

def process_order(task_id: int) -> dict:
    task = TASKS[task_id]
    task["done"] = True
    return task

def get_task(task_id: int) -> dict:
    """Retrieve a task by ID.

    Args:
        task_id: The unique identifier for the task.

    Returns:
        The task record as a dictionary.

    Raises:
        NotFoundError: If no task exists with the given ID.
    """
    if task_id not in TASKS:
        raise NotFoundError("Task")
    return TASKS[task_id]

def create_task(title: str, user_id: int, priority: int = 3) -> dict:
    """Create a new task.

    Args:
        title: The task's title.
        user_id: The ID of the user who owns the task.
        priority: The task's priority, an integer from 1 to 5. Defaults to 3.

    Returns:
        The newly created task record.

    Raises:
        ValidationError: If title is empty, user_id is not an integer, or priority
            is not an integer from 1 to 5.
        NotFoundError: If no user exists with the given user_id.
    """
    if not title or not title.strip():
        raise ValidationError("title", "cannot be empty")
    if not isinstance(user_id, int) or isinstance(user_id, bool):
        raise ValidationError("user_id", "must be an integer")
    get_user(user_id)
    _validate_priority(priority)
    new_id = max(TASKS.keys()) + 1
    TASKS[new_id] = {
        "id": new_id, "title": title, "done": False, "user_id": user_id, "priority": priority,
    }
    return TASKS[new_id]

def update_task(task_id: int, title: str | None = None, priority: int | None = None) -> dict:
    """Update a task's title and/or priority.

    Args:
        task_id: The unique identifier for the task.
        title: The new title, or None to leave it unchanged.
        priority: The new priority (1 to 5), or None to leave it unchanged.

    Returns:
        The updated task record.

    Raises:
        NotFoundError: If no task exists with the given ID.
        ValidationError: If title is empty or priority is not an integer from 1 to 5.
    """
    if task_id not in TASKS:
        raise NotFoundError("Task")
    if title is not None and not title.strip():
        raise ValidationError("title", "cannot be empty")
    if priority is not None:
        _validate_priority(priority)
    task = TASKS[task_id]
    if title is not None:
        task["title"] = title
    if priority is not None:
        task["priority"] = priority
    return task

def get_tasks_for_user(user_id: int) -> list[dict]:
    """Retrieve all tasks belonging to a user.

    Args:
        user_id: The unique identifier for the user.

    Returns:
        A list of the user's task records, empty if the user has no tasks.

    Raises:
        NotFoundError: If no user exists with the given ID.
    """
    get_user(user_id)
    return [task for task in TASKS.values() if task["user_id"] == user_id]

def list_tasks(priority: int | None = None) -> list[dict]:
    """Retrieve all tasks, optionally filtered by priority.

    Args:
        priority: Only return tasks with this priority (1 to 5), or None for all tasks.

    Returns:
        A list of task records, empty if none match.

    Raises:
        ValidationError: If priority is given and is not an integer from 1 to 5.
    """
    if priority is None:
        return list(TASKS.values())
    _validate_priority(priority)
    return [task for task in TASKS.values() if task["priority"] == priority]
