# Iteration Log

## Session 1 — 2026-10-04

### Prompt used
```
Add error handling to the get_task function in @services/tasks.py. Do not change the function signature. Run pytest -v when done.
```

Note: I accidentally ran this prompt once before with the short starter CLAUDE.md from the zip (which only says "Run tests: pytest -v") instead of my CLAUDE_v1.md. I undid that change with `git checkout services/tasks.py` and ran it again with CLAUDE_v1.md as my CLAUDE.md. The accidental run was still useful as a baseline, so I compare the two below. During the accidental run I also found out that ruff was not installed, so I installed it into the project's `.venv` with `.venv/bin/pip install ruff` before the real run.

### What Claude did
Claude read `services/tasks.py` and said it was "following the get_user pattern." It added `from utils.errors import NotFoundError` at the top and changed `get_task` so it checks `if task_id not in TASKS` and raises `NotFoundError("Task")` instead of letting a raw `KeyError` escape. It added a Google-style docstring with `Args:`, `Returns:` and `Raises:` sections that matches `get_user`, and it kept the signature `get_task(task_id: int) -> dict` the same. It also added a new test, `test_get_task_not_found_error`, to `tests/test_tasks.py` that uses `pytest.raises(NotFoundError, match="Task not found")`, and it left the existing tests unchanged. After that, it ran `pytest -v` (all 5 tests passed) and `ruff check .`. Ruff reported 6 errors, but Claude pointed out that all 6 were already in the code before the change, and it did not try to fix them. It also noticed that `process_order` has the same `KeyError` problem and asked before touching it.

What was wrong: Claude did not follow my rule to import `NotFoundError, ValidationError`. It only imported `NotFoundError` and explained that `ValidationError` is not used in this file, so ruff would flag it as an unused import. Claude was right and my rule was wrong. I did not need to send any follow-up corrections in this session.

Compared to the accidental run with the starter CLAUDE.md, the `get_task` code itself was almost the same. However, the starter run did not add a test and never ran ruff, while this run did both without me asking in the prompt.

### Observation
The Conventions rules were followed almost word for word. I noticed that `if task_id not in TASKS` and `raise NotFoundError("Task")` are exactly what I wrote in CLAUDE_v1.md, and the "New service functions get a matching test" rule and the "Run `pytest -v` and `ruff check .` before finishing any task" rule explain why this run added a test and ran ruff when the starter run did not. The one rule that was not followed was "Import errors at the top of the file: `from utils.errors import NotFoundError, ValidationError`." It was not followed because it conflicted with another rule in my own file; I asked for ruff to pass, and ruff fails on unused imports (F401). Furthermore, my lint command `ruff check .` only worked because I had already installed ruff into `.venv`. In CLAUDE_v1.md I said "install once with `pip install ruff`" and never mentioned that the project uses a virtual environment, so on a fresh copy of the project that command would not have worked.

### CLAUDE.md update
Changed the import rule in `## Conventions` from:
```
- Import errors at the top of the file: `from utils.errors import NotFoundError, ValidationError`.
```
to:
```
- Import only the error classes the file actually uses (e.g. `from utils.errors import NotFoundError`).
  Unused imports fail ruff (F401).
```
I changed this because Claude had to ignore my rule in Session 1 to keep ruff passing, and a CLAUDE.md rule that Claude has to break on purpose is a bad rule.

Changed `## Commands` from:
```
- Install: `pip install -r requirements.txt`
- Lint: `ruff check .` (install once with `pip install ruff`)
- Run `pytest -v` and `ruff check .` before finishing any task.
```
to:
```
- The project uses a virtual environment in `.venv`.
- Install: `.venv/bin/pip install -r requirements.txt ruff` (ruff lives in .venv only, not in requirements.txt)
- Lint: `.venv/bin/ruff check .`
- Run `pytest -v` and `.venv/bin/ruff check .` before finishing any task.
```
I changed this because ruff was not installed when I started and the lint command in CLAUDE_v1.md would have failed on a fresh copy of the project.

## Session 2 — 2026-10-04

### Prompt used
```
Refactor create_task in @services/tasks.py to match the style of get_user in @services/users.py exactly. Run pytest -v when done.
```

### What Claude did
Claude read both `services/tasks.py` and `services/users.py`, then added a Google-style docstring to `create_task` with `Args:`, `Returns:` and `Raises:` sections, the same way `get_user` has one. It also added a check that raises `ValidationError("title", "cannot be empty")` when the title is empty or only spaces, which copies the check `create_user` does on `name`. It changed the import line to `from utils.errors import NotFoundError, ValidationError`, which follows my updated rule to only import the error classes the file uses. The signature `create_task(title: str, user_id: int) -> dict` stayed the same, so `routes/api.py` still works. It added two new tests, `test_create_task_valid` and `test_create_task_empty_title`, at the end of `tests/test_tasks.py` without editing any of the existing tests. After that, it ran `pytest -v` (all 7 tests passed) and `ruff check .`, and it explained that the same 6 old ruff errors were still there and none of them were in `services/tasks.py`. I did not need to send any follow-up corrections.

What was wrong: I asked for a refactor, but Claude changed the behavior of `create_task`. Before, an empty title would still create a task; now the API returns a 422. Claude did tell me about this in its summary, and its reason was that the `get_user` pattern has a `Raises:` section, so it needed something to raise. Claude also noticed that `create_task` never checks if `user_id` belongs to a real user, but it did not fix that because it would mean `services/tasks.py` reaching into `services/users.py`, and it was not sure if that was allowed.

### Observation
This is my honest failure. My CLAUDE.md never said what a refactor is allowed to change, so when I said to match `get_user` "exactly," Claude decided that copying the style also meant copying the validation from `create_user`. Considering that the tests still passed, I would not have noticed the 422 change if Claude had not mentioned it. Furthermore, my Architecture section explained routes, services and the data dicts, but it said nothing about whether one service can use another, which is why Claude stopped and asked about `user_id` instead of making a decision. On the other hand, the Session 1 update worked; Claude imported `ValidationError` only because it was now used, and ruff did not report any new errors in `services/tasks.py`. I decided to keep the empty title check because it is good behavior and it has a test now, but I want future refactors to ask first.

### CLAUDE.md update
Added to `## Conventions`:
```
- "Refactor" means same behavior, new style. Do not add new validation or change what
  the API returns (e.g. a new 422) during a refactor unless the prompt asks for it.
```
I added this because Claude changed `create_task` to return a 422 for empty titles during what I asked to be a refactor, and nothing in my CLAUDE.md said that was not allowed.

Added to `## Architecture`:
```
- Services may call each other's functions, not each other's data. To check a user
  exists from `services/tasks.py`, call `get_user(user_id)` (it raises `NotFoundError`).
  Never import or read `USERS` outside `services/users.py`.
```
I added this because Claude did not know if `services/tasks.py` was allowed to check `user_id` against `services/users.py`, and Session 3 is about tasks for a `user_id`, so I wanted the answer written down before then.

## Session 3 — 2026-10-04

### Prompt used
```
Add a new function to @services/tasks.py that returns all tasks for a given user_id. Follow the same pattern as the existing functions. Add a test for it. Run pytest -v when done.
```

### What Claude did
Claude added `get_tasks_for_user(user_id: int) -> list[dict]` to `services/tasks.py` with a Google-style docstring that has the same `Args:`, `Returns:` and `Raises:` sections as the other functions. Instead of reading the `USERS` dict, it calls `get_user(user_id)` first, so an unknown user raises `NotFoundError("User")` and the API would return a 404, while a real user with no tasks just gets an empty list. It added two tests to `tests/test_tasks.py`: `test_get_tasks_for_user_valid`, which checks that user 1 gets tasks 1 and 2, and `test_get_tasks_for_user_not_found_error`, which checks that user 999 raises `NotFoundError` with "User not found". It did not change `get_task`, `create_task` or any existing tests. After that, it ran `pytest -v` (all 9 tests passed) and `ruff check .`, and it explained that the same 6 old ruff errors were still there and none were in `services/tasks.py`. It also did not add an API route on its own because I did not ask for one. I did not need to send any follow-up corrections, and Claude did not need me to make any decisions.

The one thing I noticed was in the test. Claude wrote `test_get_tasks_for_user_valid` so it allows extra tasks for user 1, and it explained that this was because `test_create_task_valid` from Session 2 adds another task for user 1 earlier in the test run. The test still works, but it is weaker than it could be because of how the tests share data.

### Observation
The rule I added after Session 2 worked exactly how I wanted. Claude wrote that it called `get_user(user_id)` "as CLAUDE.md requires, instead of reading USERS," which is almost the same wording as my Architecture rule. In Session 2, Claude stopped and asked me about checking `user_id`; in Session 3, it already knew the answer. However, the test issue showed me something about task-manager that my CLAUDE.md did not explain. `TASKS` is a module-level dict, so every test shares it, and a test that calls `create_task` changes the data for every test after it. Claude figured this out by itself this time, but a future session could easily write a test that checks for an exact list of tasks and fails depending on the order the tests run in.

### CLAUDE.md update
Added to `## Conventions`:
```
- Tests share the module-level `TASKS` dict, and `test_create_task_valid` adds a task for
  user 1. Assert on the seed ids (1-3), not exact counts or full lists.
```
I added this because in Session 3 Claude had to work around `test_create_task_valid` adding an extra task for user 1, and I want future sessions to know about the shared data before they write a test, not after.

## Improvement across sessions
I did not need to send any follow-up corrections in any of the three sessions, so I compared the number of problems I had to deal with after each session. In Session 1, Claude had to break one of my rules (the `NotFoundError, ValidationError` import) because it conflicted with ruff, and my lint command did not work on a fresh copy of the project. In Session 2, Claude changed the behavior of `create_task` during a refactor and had to stop and ask me whether `services/tasks.py` could check `user_id`. In Session 3, Claude followed every rule, did not change anything I did not ask for, and did not need me to decide anything. All in all, the problems went from two in Session 1, to two in Session 2, to zero in Session 3, and each problem from Sessions 1 and 2 turned into a rule that Claude followed in the next session.
