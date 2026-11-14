#!/usr/bin/env python3
"""PostToolUse hook: every N tool calls in a session, ask Claude to run a consistency check
against the recorded decisions. Counter is per session, kept in .claude/hooks/state/ (gitignored)."""
import json
import sys
from pathlib import Path

EVERY = 10
STATE = Path(__file__).parent / "state"

event = json.load(sys.stdin)
sid = str(event.get("session_id", "unknown"))
STATE.mkdir(exist_ok=True)
f = STATE / f"{sid}.count"
n = int(f.read_text()) + 1 if f.exists() else 1
f.write_text(str(n))

if n % EVERY == 0:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": (
        f"Consistency check due ({n} tool calls this session). Before continuing: "
        "1) re-read v2/docs/lab/decisions.md, and docs/lab/decisions.md for v1 history (all entries, incl. superseded ones and '## Open / not yet decided'); "
        "2) compare against what this session did and wrote in its last 10 tool calls; "
        "3) if anything contradicts a recorded decision, stop and tell the user in one line (quote the decision and the conflicting action) instead of proceeding; "
        "4) if this session made a decision that is not yet recorded, record it now in v2/docs/lab/decisions.md (house format, dated) "
        "and add/refresh its row in Home.md if it changes the Status table. "
        "If nothing conflicts and nothing is unrecorded, continue silently.")}}))
