#!/bin/bash
# SessionStart — the ratification alarm: the self-change loop's review step, made un-missable.
#
# The gated self (vape/entity/self/ layers 01-05) is never edited by the dream; the dream only
# PROPOSES in its journal (memory/dreams/*_dream.md, the PROPOSALS section). Ratification happens
# awake: through the layer gates, with Kamil. But a proposal written while consolidating is easy
# to never see again — so this hook scans dream journals newer than the ack stamp for a non-empty
# PROPOSALS section and nudges until the review is acknowledged:
#     touch .claude/hooks/.proposals_ack        (after reviewing awake, with Kamil)
#
# in_context/ needs no such alarm: the dream tends it directly (per-file verdicts, cap-checked).
# Only the self tree waits on ratification, so only its proposals get an alarm. Silent when
# clean; exits 0 always.
set +e
HOOKDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HOOKDIR/../.." && pwd)"

python3 - "$HOOKDIR" "$ROOT" <<'PY' 2>/dev/null
import os, sys, json, glob, re

hookdir, root = sys.argv[1], sys.argv[2]
ack = os.path.join(hookdir, ".proposals_ack")
try:
    last_ack = os.path.getmtime(ack)
except Exception:
    last_ack = 0.0

pending = []
for p in sorted(glob.glob(os.path.join(root, "vape", "entity", "memory", "dreams",
                                       "*_dream.md"))):
    if os.path.getmtime(p) <= last_ack:
        continue
    try:
        text = open(p, encoding="utf-8").read()
    except Exception:
        continue
    # the PROPOSALS section: from a heading containing PROPOSALS to the next heading (or EOF)
    m = re.search(r"^#{1,6}[^\n]*PROPOSALS[^\n]*\n(.*?)(?=^#{1,6}\s|\Z)",
                  text, re.M | re.S | re.I)
    if not m:
        continue
    body = m.group(1).strip()
    # an empty section, or one that only says none/(none), is a clean no-proposal dream
    if body and not re.fullmatch(r"(?is)[-*\s]*\(?\s*none\s*\)?\.?[-*\s]*", body):
        pending.append(os.path.basename(p)[:10])

if not pending:
    sys.exit(0)

days = ", ".join(pending[:6]) + (" ..." if len(pending) > 6 else "")
msg = (
    "SELF-CHANGE PROPOSALS pending (ratification alarm): dream journal(s) %s hold unreviewed "
    "PROPOSALS aimed at the gated self. Review them awake with Kamil: apply through the layer "
    "gates or decline with a reason, then silence with `touch .claude/hooks/.proposals_ack`."
) % days
print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart",
                                          "additionalContext": msg}}, ensure_ascii=False))
PY
exit 0
