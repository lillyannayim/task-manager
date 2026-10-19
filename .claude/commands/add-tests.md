# Use to add missing tests for one existing service function; not for fixing failing tests or testing routes.

Goal: Write pytest tests for the service function `$ARGUMENTS`. Put them in
`tests/test_tasks.py` if the function lives in `services/tasks.py`, or in
`tests/test_users.py` if it lives in `services/users.py`.

Context:
- Read the function and its docstring first. Write one test for the happy path and one
  test for each error listed under `Raises:` (use `pytest.raises(NotFoundError)` or
  `pytest.raises(ValidationError)` from `utils/errors.py`).
- Tests share the module-level `TASKS` dict. `tests/conftest.py` restores `TASKS` after
  each test, and `tests/test_users.py` has its own fixture that restores `USERS`.
- `test_create_task_valid` adds a task for user 1, so assert on the seed ids
  (tasks 1-3, users 1-2), not on exact counts or full lists.

Constraints:
- Only add new test functions. Do not edit or delete existing tests.
- Already covered: if tests for the happy path and every `Raises:` case already exist,
  add nothing. Report which existing tests cover each case instead.
- Do not change any code in `services/`. If a test fails because of a real bug, stop and
  report the bug instead of changing the code or weakening the test.
- Do not touch `tests/conftest.py`.
- Name each test `test_<function>_<case>`, for example `test_list_tasks_invalid_priority`.

Verification:
- Run `pytest -q` after adding the tests; all tests must pass.
- Run `.venv/bin/ruff check tests/` and confirm you added no new errors.
- Report how many tests you added and which `Raises:` cases each one covers.
