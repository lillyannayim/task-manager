# Task Manager
Python Flask API for managing tasks and users. Data is stored in memory (no database).

## Commands
- Install: `pip install -r requirements.txt`
- Run all tests: `pytest -v`
- Run task tests only: `pytest tests/test_tasks.py -v`
- Lint: `ruff check .` (install once with `pip install ruff`)
- Run `pytest -v` and `ruff check .` before finishing any task.

## Architecture
Layered: `routes/api.py` → `services/*.py` → in-memory data dicts.
- `routes/api.py`: HTTP only. A Flask `Blueprint` named `api` that parses the
  request, calls a service, and returns `jsonify(...)`. No business logic here.
- `handle_app_error` in `routes/api.py` turns any `AppError` into
  `{"error": message}` with its `status_code`. A raw exception becomes a 500 instead.
- `services/tasks.py` and `services/users.py`: all business logic and validation.
- Data layer: the module-level `TASKS` and `USERS` dicts (keyed by int id) act as
  the repository. There is no `repositories/` package; do not create one.
- `utils/errors.py`: `AppError` base class with `status_code`, plus
  `NotFoundError` (404) and `ValidationError` (422).
- Canonical example of a service function: `get_user` in `services/users.py`.

## Conventions
- Follow `services/users.py` as the pattern for every service function.
- In `services/`: type hints on every parameter and return value (e.g. `def get_task(task_id: int) -> dict:`).
- Google-style docstrings with `Args:`, `Returns:` and `Raises:` sections,
  exactly like `get_user` and `create_user`.
- Errors: raise `AppError` subclasses from `utils/errors.py`, never raw exceptions.
  - Missing record → `raise NotFoundError("Task")` (check `if task_id not in TASKS`
    first, never let a raw `KeyError` escape from `TASKS[task_id]`).
  - Bad input → `raise ValidationError("<field>", "<reason>")`,
    as in `create_user`.
- Import errors at the top of the file: `from utils.errors import NotFoundError, ValidationError`.
- New service functions get a matching test in `tests/test_tasks.py`.

## Do not touch
- Do not change the signatures of existing functions in `services/tasks.py`
  (`process_order`, `get_task`, `create_task`) or `services/users.py`.
  `routes/api.py` and `tests/test_tasks.py` call them as-is.
- Do not rename `process_order`. It marks a task as done; the name is legacy,
  but `routes/api.py` imports it by name.
- Do not edit `utils/errors.py` status codes (404, 422) or constructor arguments.
  API responses depend on them.
- Do not change the seed records in `TASKS` (ids 1-3) or `USERS` (ids 1-2).
  Tests depend on them.
- Do not edit existing tests in `tests/test_tasks.py` to make them pass. Fix the code instead.
- Do not add packages to `requirements.txt` (pinned: `flask==3.0.0`, `pytest==8.0.0`)
  or add a database.
