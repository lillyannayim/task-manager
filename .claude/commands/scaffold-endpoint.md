# Use to add one new REST endpoint for a resource; not for changing or refactoring existing routes.

Arguments: $ARGUMENTS
The first word is the resource name (for example `tags`) and the second word is the HTTP
method (GET, POST, PATCH or DELETE).

Goal: Scaffold the endpoint for that resource and method by creating or updating exactly
these files:
- Route file: `routes/api.py` (add one route function on the existing `api` Blueprint).
- Service file: `services/<resource>.py` (create it if it does not exist) with one
  service function the route calls.
- Schema file: the record schema in this repo is the module-level `<RESOURCE>` dict
  (keyed by int id) at the top of `services/<resource>.py`, like `TASKS` in
  `services/tasks.py`. Define the record fields there. There is no `schemas/` package;
  do not create one.
- Test file: `tests/test_api.py` (add one happy-path test).

Context:
- `routes/api.py` is the canonical route pattern (this repo has no `routes/tasks.py`).
  Copy `create_task_route` for POST and `get_task_route` for GET.
- Copy `services/tasks.py` for the service function: type hints, Google-style docstring
  with `Args:`, `Returns:` and `Raises:`, and errors raised as `NotFoundError` or
  `ValidationError` from `utils/errors.py`.
- `tests/test_api.py` shows how the existing tests build the Flask test client.

Constraints:
- No business logic in the route handler. It may only read the request, call one
  service function and return `jsonify(...)` with a status code. All validation and
  lookups go in the service function.
- Read the JSON body with `request.get_json(silent=True) or {}` so a request with a missing
  or invalid body still reaches the service function and returns its 422, instead of failing
  inside Flask before the service runs.
- Do not reorder or reformat the import block in `routes/api.py`; add a new
  `from services.<resource> import ...` line directly after the existing services imports.
- Do not edit existing routes, existing service functions or existing tests.
- Do not touch `utils/errors.py`, `requirements.txt` or `tests/conftest.py`.

Verification:
- Run `pytest -q`; every test must pass.
- The new happy-path test must call the new endpoint with the test client and assert the
  correct status: 201 for POST, 200 for GET and PATCH, 200 or 204 for DELETE.
- Run `.venv/bin/ruff check .` and confirm you added no new errors.
