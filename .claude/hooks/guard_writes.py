#!/usr/bin/env python3
"""PreToolUse guard for task-manager.

Claude Code runs this script before every Write, Edit, MultiEdit and Bash tool
call (see the matcher in .claude/settings.json). It reads the tool call as JSON
on stdin. Exit 0 lets the call run. Exit 2 blocks it, and the message printed to
stderr is shown to Claude so it knows why.

Three guards:
  1. Path guard    (Write/Edit/MultiEdit, and Bash commands that write files):
     blocks edits to BLOCKED_PATHS, ignoring upper/lower case.
  2. Bash guard    (Bash): blocks commands matching BLOCKED_COMMANDS.
  3. Content guard (Write/Edit/MultiEdit): blocks hardcoded database connection
     strings in CONTENT_CHECKED_PATHS.

To add a rule, add an entry to the matching list below, then run
`pytest -q` and try the blocked action once in Claude Code to confirm it fires.
"""
import json
import os
import re
import sys

# Files Claude may never write to, as paths relative to the repo root.
# Week 7 note: these same rules should also apply to MCP tool calls
# (tool names like mcp__<server>__<tool>) that can write files, for example a
# filesystem or GitHub MCP server, so a write to utils/errors.py through MCP is
# blocked too. All three entries below should carry over.
BLOCKED_PATHS = {
    "utils/errors.py": "status codes and constructor arguments are part of the API contract",
    "requirements.txt": "dependencies are pinned (flask==3.0.0, pytest==8.0.0); do not add packages",
    "tests/conftest.py": "the shared TASKS fixture is only changed when a prompt asks for it",
}

# Bash patterns that are never allowed. Each is (regex, reason).
# \b word boundaries keep these from matching inside longer words
# (for example "DROP TABLES_LOG" or "farm -rfx").
BLOCKED_COMMANDS = [
    (r"\b(DROP|TRUNCATE)\s+TABLE\b", "destructive SQL (DROP/TRUNCATE TABLE)"),
    (r"\brm\s+(-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*|-[a-zA-Z]*f[a-zA-Z]*r[a-zA-Z]*)(\s|$)",
     "recursive force delete (rm -rf)"),
    (r"\bgit\s+push\b.*(\s--force(-with-lease)?\b|\s-f\b)",
     "git force-push rewrites history on GitHub"),
]

# Files Claude may write, but whose new content is checked.
CONTENT_CHECKED_PATHS = {"services/tasks.py", "services/users.py"}
CONNECTION_STRING = re.compile(r"postgresql://|sqlite:///")


def block(message: str) -> None:
    print(f"BLOCKED by guard_writes.py: {message}", file=sys.stderr)
    sys.exit(2)


def relative_path(file_path: str, cwd: str) -> str:
    """Turn the tool's file_path into a repo-relative, lowercase path like utils/errors.py.

    Lowercasing matters because macOS ignores case: Utils/errors.py and
    utils/errors.py are the same file (Vector 1 in HOOK_LOG.md).
    """
    root = os.environ.get("CLAUDE_PROJECT_DIR") or cwd or os.getcwd()
    if os.path.isabs(file_path):
        file_path = os.path.relpath(file_path, root)
    return os.path.normpath(file_path).replace(os.sep, "/").casefold()


# Bash commands that can write to a file: redirection, tee, sed/perl -i,
# mv, cp, rm, truncate, dd, ln, and inline python. Used with the path check
# so read-only commands like `cat utils/errors.py` are still allowed.
WRITE_IN_BASH = re.compile(
    r">|\btee\b|\b(sed|perl)\b[^|;&]*\s-i|\b(mv|cp|rm|truncate|dd|ln|install)\b|\bpython3?\s+-c\b",
    re.IGNORECASE,
)


def bash_writes_blocked_path(command: str):
    """Return the protected path a Bash command would write to, if any (Vector 2)."""
    cleaned = re.sub(r"\d?>&\d|[12]?>\s*/dev/null", " ", command)  # 2>&1 and >/dev/null are not file writes
    lowered = cleaned.casefold()
    for path in BLOCKED_PATHS:
        if path.casefold() in lowered and WRITE_IN_BASH.search(cleaned):
            return path
    return None


def new_content(tool_name: str, tool_input: dict) -> str:
    if tool_name == "Write":
        return tool_input.get("content", "")
    if tool_name == "Edit":
        return tool_input.get("new_string", "")
    if tool_name == "MultiEdit":
        return "\n".join(e.get("new_string", "") for e in tool_input.get("edits", []))
    return ""


def main() -> None:
    event = json.load(sys.stdin)
    tool_name = event.get("tool_name", "")
    tool_input = event.get("tool_input", {})

    if tool_name == "Bash":
        command = tool_input.get("command", "")
        for pattern, reason in BLOCKED_COMMANDS:
            if re.search(pattern, command, re.IGNORECASE):
                block(f"command not allowed: {reason}.")
        path = bash_writes_blocked_path(command)
        if path:
            block(f"this command would write to {path}, which is protected: {BLOCKED_PATHS[path]}.")
        sys.exit(0)

    if tool_name in ("Write", "Edit", "MultiEdit"):
        path = relative_path(tool_input.get("file_path", ""), event.get("cwd", ""))
        if path in BLOCKED_PATHS:
            block(f"{path} is protected: {BLOCKED_PATHS[path]}.")
        if path in {p.casefold() for p in CONTENT_CHECKED_PATHS} and CONNECTION_STRING.search(new_content(tool_name, tool_input)):
            block(
                f"{path} would contain a hardcoded database connection string. "
                "Connection strings must come from environment variables "
                "(for example os.environ['DATABASE_URL']), never from source code."
            )

    sys.exit(0)


if __name__ == "__main__":
    main()
