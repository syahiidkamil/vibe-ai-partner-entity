#!/bin/bash
# SessionStart — the ratification alarm: the self-change loop's review step, made un-missable.
#
# The gated self (vape/entity/self/ layers 01-05) is never edited by the dream; anything
# identity-adjacent becomes ONE FILE in memory/proposals/pending/ (the dream's hard frame; awake
# Saori may file one too). This hook simply reports whether that inbox is empty. The folder IS
# the state machine — no regex over journals, no ack stamp: reviewing a proposal (awake, with
# Kamil: layer gate + recurrence + lion) ends by appending the verdict and moving the file to
# memory/proposals/resolved/, and an empty pending/ is what silences the alarm.
#
# in_context/ needs no such alarm: the dream tends it directly. Only the gated self waits on
# ratification, so only its proposals get one. Silent when clean; exits 0 always.
set +e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

python3 - "$ROOT" <<'PY' 2>/dev/null
import os, sys, json, glob

root = sys.argv[1]
pending = sorted(glob.glob(os.path.join(root, "vape", "entity", "memory", "proposals",
                                        "pending", "*.md")))
if not pending:
    sys.exit(0)

names = ", ".join(os.path.basename(p)[:-3] for p in pending[:5])
if len(pending) > 5:
    names += " ..."
msg = (
    "SELF-CHANGE PROPOSALS pending (ratification alarm): %d open in memory/proposals/pending/ "
    "(%s). Review awake with Kamil: walk the target layer's gate + the recurrence test + the "
    "lion, apply by hand (opening a growth/change_evals entry) or decline, append the verdict, "
    "and move the file to memory/proposals/resolved/. The alarm silences itself when pending/ "
    "is empty."
) % (len(pending), names)
print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart",
                                          "additionalContext": msg}}, ensure_ascii=False))
PY
exit 0
