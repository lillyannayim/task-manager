# Task 2 — Subagent Decomposition: Notification Preferences

Feature: a user can set `notification_pref` to `email`, `sms`, or `none` (default `none`).
PATCH /users/{id}/notifications updates it (invalid values raise `ValidationError`, 422),
GET /users/{id}/notifications returns it, and the existing user detail endpoint
(GET /users/{id}) includes `notification_pref` in its response. The codebase has no user
list endpoint, so there is no list response to update; no subagent adds one.

Design decisions made before running:
- The allowed values live in one constant, `VALID_NOTIFICATION_PREFS = ("email", "sms", "none")`,
  in services/users.py. Every user record stores the key `notification_pref`, defaulting to `"none"`.
- Baseline before SA-1: `pytest -q` shows 51 passed, and `.venv/bin/ruff check .` shows 6
  pre-existing errors (in app.py, routes/api.py and tests/test_tasks.py). No subagent fixes them.

## Decomposition Table

| Subagent # | Input | Task | Output | Constraint | Hand-off |
|---|---|---|---|---|---|
| SA-1: Data layer | CLAUDE.md, services/users.py | Add the `notification_pref` field (default `"none"`) to every user record and add the `VALID_NOTIFICATION_PREFS` constant. | services/users.py (modified) | Do not touch routes/api.py, services/tasks.py, utils/errors.py, or anything in tests/. The only function change allowed is setting the default in `create_user`; do not add new functions. | Both seed users in `USERS` and any user returned by `create_user` have `notification_pref == "none"`; `VALID_NOTIFICATION_PREFS` is importable from services/users.py. |
| SA-2: Service layer | CLAUDE.md, services/users.py, utils/errors.py | Add `get_notification_pref(user_id)` and `update_notification_pref(user_id, pref)` following the `get_user` pattern. | services/users.py (modified) | Do not touch routes/api.py, services/tasks.py, utils/errors.py, or tests/. Never return Flask responses, `jsonify`, or HTTP status codes from services/users.py; raise `NotFoundError` for a missing user and `ValidationError` for a value not in `VALID_NOTIFICATION_PREFS`. | Two service functions with type hints and Google-style docstrings; `update_notification_pref` returns the new pref string; both raise only `AppError` subclasses from utils/errors.py. |
| SA-3: API layer | CLAUDE.md, routes/api.py, services/users.py (read only) | Add GET and PATCH /users/{id}/notifications that call the SA-2 service functions. | routes/api.py (modified) | Do not touch anything in services/, utils/errors.py, or tests/. No validation logic in routes/api.py; the route reads the JSON body, calls the service, and returns the result. Do not add a user list endpoint. | GET returns `{"notification_pref": <value>}` with 200; PATCH takes `{"notification_pref": <value>}` and returns the same shape with 200; invalid value returns 422 `{"error": ...}` via `handle_app_error`; unknown user returns 404. GET /users/{id} already includes the field because it returns the user dict. |
| SA-4: Tests | CLAUDE.md, services/users.py, routes/api.py, tests/conftest.py and tests/test_api.py (for fixture and test style only) | Write tests covering the service functions and both endpoints, including the default value and invalid input. | tests/test_users.py (new) | Only create tests/test_users.py. Do not modify services/, routes/, utils/, tests/conftest.py, tests/test_api.py, or tests/test_tasks.py. If a test fails because of a bug in application code, stop and report it instead of changing application code. | `pytest -q` passes with the new tests; tests/test_users.py has its own `client` fixture and an autouse fixture that saves and restores `USERS`, so it does not affect other tests. |

## Exact Prompts

Run each one in a fresh session (`/exit` and relaunch `claude`, or `/clear`, between them). Plan Mode is not used for Task 2.

### SA-1 prompt
```
Goal: Add a notification_pref field to user records in @services/users.py.
Both seed users in USERS and every user created by create_user must have
notification_pref set to "none". Add a module-level constant
VALID_NOTIFICATION_PREFS = ("email", "sms", "none").
Constraints: Only edit services/users.py. Do not touch routes/api.py,
services/tasks.py, utils/errors.py, or anything in tests/. The only function
change allowed is setting the default in create_user; do not add new functions.
Ruff already reports 6 pre-existing errors in other files; do not fix them.
Verification: Run pytest -q when done and report the result.
```

### SA-2 prompt
```
Goal: Add two functions to @services/users.py: get_notification_pref(user_id)
and update_notification_pref(user_id, pref). Follow the existing get_user
pattern exactly, including type hints and Google-style docstrings.
Context: Errors come from @utils/errors.py. Raise NotFoundError("User") if the
user does not exist. Raise ValidationError if pref is not in
VALID_NOTIFICATION_PREFS. update_notification_pref returns the new pref string.
Constraints: Only edit services/users.py. Do not touch routes/api.py,
services/tasks.py, utils/errors.py, or tests/. Never return Flask responses,
jsonify, or HTTP status codes from this file; signal errors only by raising
AppError subclasses. Ruff already reports 6 pre-existing errors in other
files; do not fix them.
Verification: Run pytest -q when done and report the result.
```

### SA-3 prompt
```
Goal: In @routes/api.py, add GET /users/<int:user_id>/notifications and
PATCH /users/<int:user_id>/notifications. GET returns
{"notification_pref": value}. PATCH reads notification_pref from the JSON body
with data.get("notification_pref"), calls update_notification_pref, and
returns {"notification_pref": value}.
Context: The service functions are get_notification_pref and
update_notification_pref in @services/users.py. Errors are handled by the
existing handle_app_error. GET /users/<id> already returns the full user dict,
which now includes notification_pref. There is no user list endpoint; do not
add one.
Constraints: Only edit routes/api.py. Do not touch anything in services/,
utils/errors.py, or tests/. Put no validation logic in the route; let
ValidationError and NotFoundError propagate to handle_app_error. In the
import block, only add the names you need; do not reformat or reorder
existing import lines. Ruff already reports 6 pre-existing errors, 2 of them
in routes/api.py; do not fix them, only make sure there are no new ones.
Verification: Run pytest -q when done and report the result.
```

### SA-4 prompt
```
Goal: Create tests/test_users.py with tests for the notification preference
feature: both seed users default to "none", get_notification_pref and
update_notification_pref work, an invalid value raises ValidationError, a
missing user raises NotFoundError, GET and PATCH /api/users/<id>/notifications
return the right status codes and bodies (200, 422 for an invalid value, 404
for an unknown user), and GET /api/users/<id> includes notification_pref.
Context: Code under test is in @services/users.py and @routes/api.py. Follow
the style of @tests/test_api.py. @tests/conftest.py only restores TASKS, and
the client fixture is defined inside tests/test_api.py, so this file needs its
own client fixture and its own autouse fixture that saves a deep copy of USERS
and restores it after each test.
Constraints: Only create tests/test_users.py. Do not modify services/,
routes/, utils/, tests/conftest.py, tests/test_api.py, or tests/test_tasks.py.
If a test fails because of a bug in application code, stop and tell me
instead of editing application code. Ruff already reports 6 pre-existing
errors in other files; do not fix them.
Verification: Run pytest -q when done and report the result.
```

## Verification Log

| Subagent | pytest -q result | Fix needed in same session? |
|---|---|---|
| Baseline | 51 passed | — |
| SA-1 | _fill in_ | _fill in_ |
| SA-2 | _fill in_ | _fill in_ |
| SA-3 | _fill in_ | _fill in_ |
| SA-4 | _fill in_ | _fill in_ |

## Divergence

_Fill in after all four subagents have run._

**Did Claude follow the constraint field for every subagent?**

**Did any subagent's output break the next subagent's assumption? How did you recover?**

**Would you write the decomposition differently a second time? What would you change?**
