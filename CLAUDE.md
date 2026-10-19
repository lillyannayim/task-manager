# Task Manager
Python Flask API for managing tasks and users. Data is stored in memory (no database).

## Commands
- The project uses a virtual environment in `.venv`.
- Install: `.venv/bin/pip install -r requirements.txt ruff` (ruff lives in .venv only, not in requirements.txt)
- Run all tests: `pytest -v`
- Run task tests only: `pytest tests/test_tasks.py -v`
- Quick check after each step or subagent: `pytest -q`
- Lint: `.venv/bin/ruff check .`
- Run `pytest -v` and `.venv/bin/ruff check .` before finishing any task.
- Ruff currently reports 6 pre-existing errors (in `app.py`, `routes/api.py` and `tests/test_tasks.py`).
  Only make sure you add no new ones; do not fix the existing ones unless the prompt asks.
- Slash commands (in `.claude/commands/`):
  - `/audit-errors <file>`: make every function in one `services/` file raise `AppError` subclasses
    instead of raw exceptions; skips functions that are already correct (e.g. `/audit-errors services/tasks.py`).
  - `/scaffold-endpoint <resource> <METHOD>`: add one new endpoint across `routes/api.py`,
    `services/<resource>.py` and `tests/test_api.py` (e.g. `/scaffold-endpoint tags POST`).
  - `/add-tests <function>`: add happy-path and `Raises:` tests for one existing service function
    without changing code; adds nothing if it is already covered (e.g. `/add-tests process_order`).

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
- Services may call each other's functions, not each other's data. To check a user
  exists from `services/tasks.py`, call `get_user(user_id)` (it raises `NotFoundError`).
  Never import or read `USERS` outside `services/users.py`.
- Boundary between `services/` and `routes/`: functions in `services/` never import Flask or return
  `jsonify`, responses or status codes and signal every error by raising an `AppError` subclass, the way
  `get_user` in `services/users.py` does, while each route in `routes/api.py` only reads the request,
  calls one service function and returns its result.

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
- Import only the error classes the file actually uses (e.g. `from utils.errors import NotFoundError`).
  Unused imports fail ruff (F401).
- New service functions get a matching test in `tests/test_tasks.py`.
- Tests share the module-level `TASKS` dict, and `test_create_task_valid` adds a task for
  user 1. Assert on the seed ids (1-3), not exact counts or full lists.
- "Refactor" means same behavior, new style. Do not add new validation or change what
  the API returns (e.g. a new 422) during a refactor unless the prompt asks for it.

## Do not touch
- Do not change the signatures of existing functions in `services/tasks.py`
  (`process_order`, `get_task`, `create_task`) or `services/users.py`.
  `routes/api.py` and `tests/test_tasks.py` call them as-is.
- Do not rename `process_order`. It marks a task as done; the name is legacy,
  but `routes/api.py` imports it by name.
- Do not change the seed records in `TASKS` (ids 1-3) or `USERS` (ids 1-2).
  Tests depend on them.
- Do not edit existing tests in `tests/test_tasks.py` to make them pass. Fix the code instead.
- Do not add a database.
- Do not reformat or reorder the import block in `routes/api.py`. To import a new name,
  add it to the end of the existing `from services... import` line.
- Do not reformat existing lines in `services/tasks.py` or `services/users.py` (for example the
  record dicts in `create_task` and `create_user`); change only the lines the task needs.
- When a prompt limits edits to `services/`, do not create or edit anything in `tests/` to satisfy
  the test rule above; report which functions still need tests instead.

## Hooks
`.claude/hooks/guard_writes.py` is a PreToolUse hook, registered in `.claude/settings.json` with the
matcher `Write|Edit|MultiEdit|Bash`, that runs before each of those tool calls and blocks the call by
exiting with code 2 and printing the reason, which Claude sees. It never lets Claude write
`utils/errors.py`, `requirements.txt` or `tests/conftest.py` (`BLOCKED_PATHS`), in any capitalization and
through Bash writes such as `>`, `sed -i`, `mv` or `cp` as well as the Edit tools, so a person edits those
files by hand. It also blocks the Bash patterns `DROP TABLE`/`TRUNCATE TABLE`, `rm -rf` and
`git push --force` (`BLOCKED_COMMANDS`), and any write to `services/tasks.py` or `services/users.py` that
contains a `postgresql://` or `sqlite:///` connection string (`CONTENT_CHECKED_PATHS`). To add a rule, add
a path and reason to `BLOCKED_PATHS`, a `(regex, reason)` pair using `\b` word boundaries to
`BLOCKED_COMMANDS`, or a path to `CONTENT_CHECKED_PATHS`, then test it with
`echo '<tool call JSON>' | python3 .claude/hooks/guard_writes.py; echo "exit=$?"` (`exit=2` means blocked;
HOOK_LOG.md has example JSON) and run `pytest -q`.
