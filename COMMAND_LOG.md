# COMMAND_LOG.md

Week 6, Task 1. Each command was run in Claude Code on task-manager, then checked with
`git diff --stat`, `git status --short`, `pytest -q` and `.venv/bin/ruff check .`.

Note on the handout: it names `routes/tasks.py` as the canonical route pattern, but this repo
keeps every route in `routes/api.py` and has no `schemas/` package, so `scaffold-endpoint.md`
points at `routes/api.py` and treats the module-level data dict in the service file as the schema.

| Command invoked | $ARGUMENTS used | Stayed in scope? | What worked or what I changed |
|---|---|---|---|
| `/audit-errors` | `services/tasks.py` | Yes | The idempotency constraint worked; Claude fixed only `process_order` (added the `if task_id not in TASKS: raise NotFoundError("Task")` check and a docstring, 13 lines) and skipped every function that already used `AppError`, and because the Verification step made it run ruff it also noticed the count had gone from 6 to 7 because of EXE001 in my new hook, which I fixed with `chmod +x .claude/hooks/guard_writes.py`. |
| `/scaffold-endpoint` | `tags POST` | Yes | Claude touched exactly `routes/api.py`, `tests/test_api.py` and a new `services/tags.py` (66 tests passed, ruff still 6), and it added a `restore_tags` fixture on its own because `conftest.py` only resets `TASKS`; however, it pointed out that a POST with no JSON body fails inside Flask before reaching `create_tag`, so I added a constraint telling it to read the body with `request.get_json(silent=True) or {}` so a missing body reaches the service and returns a 422. |
| `/add-tests` | `process_order` | Yes | The first run added `test_process_order_not_found_error` (1 file, 4 lines, 67 tests passed) and the second run added nothing because the happy path and the one `Raises:` case were already covered; since that skip only came from Claude's own judgment, I added an explicit "already covered, add nothing" constraint like the idempotency rule in `audit-errors.md`. |
