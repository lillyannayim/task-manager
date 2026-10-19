# Use to bring every function in one services/ file up to the AppError pattern; not for routes/, tests/ or adding new behavior.

Goal: Audit error handling in @$ARGUMENTS and fix every function that can raise a raw
exception (for example a KeyError from `TASKS[task_id]`) so it raises an `AppError`
subclass from `utils/errors.py` instead.

Context:
- `utils/errors.py` defines `AppError`, `NotFoundError(resource)` (404) and
  `ValidationError(field, reason)` (422).
- The pattern to copy is `get_user` in @services/users.py and `get_task` in
  @services/tasks.py: check `if task_id not in TASKS: raise NotFoundError("Task")`
  before indexing, and give the function a Google-style docstring with `Args:`,
  `Returns:` and `Raises:` sections.
- `handle_app_error` in `routes/api.py` turns an `AppError` into a JSON error with its
  status code; a raw exception becomes a 500, which is the bug this audit removes.

Constraints:
- Idempotency: if a function already checks its inputs and raises the correct `AppError`
  subclass (like `get_task` and `update_task`), skip it. Do not rewrite, reformat or
  re-document it. Running this command twice on the same file must change nothing the
  second time.
- Only edit $ARGUMENTS. Do not touch `utils/errors.py`, `routes/api.py`,
  `tests/test_tasks.py` or `tests/conftest.py`.
- Do not change any function's name or signature (`process_order` keeps its name).
- Import only the error classes the file actually uses (ruff F401).
- Do not add new validation beyond what is needed to stop a raw exception escaping.

Verification:
- After every function you change, run `pytest -q` and `.venv/bin/ruff check $ARGUMENTS`
  before moving to the next function. Stop and report if a test fails.
- At the end, list each function in the file as either "fixed" or "skipped (already
  correct)".
