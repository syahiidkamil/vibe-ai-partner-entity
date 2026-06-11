#!/bin/bash
# SessionStart hook — temporal-self freshness check, deterministic archive, RIPPLE directive.
#
# Fires on session start (startup / resume / clear). It:
#   1. Grounds the date + days-alive.
#   2. Reads the manifest current_temporal_self_date.json. Keys are day-granular and self-contained:
#        daily         : YYYY-MM-DD
#        weekly        : YYYY-MM-W{w}-D{d}
#        monthly       : YYYY-MM-W{w}-D{d}
#        yearly        : YYYY-MM-W{w}-D{d}
#        autobiography : YYYY-MM-W{w}-D{d}
#      (W1=1-7, W2=8-14, W3=15-21, W4=22-end; D = day-within-week.)
#   3. RIPPLE model — a new day is a stone dropped; it ripples UP through every scale, each one
#      touched but leaner as it rises:
#        ROLLOVER : a scale's own period part is OLDER than now (ordered compare) -> archive+fresh.
#        RIPPLE   : same period, but the full key DIFFERS from now (equality) -> rewrite in place,
#                   leaner the higher it goes. Every new day ripples weekly->monthly->yearly->
#                   autobiography. Autobiography never rolls over; it only ripples.
#   4. On a new day it DETERMINISTICALLY archives the rolled-over daily_self to past_daily_/ in bash
#      (data-safety). All other archiving + the prose ripple is the subagent's job (a NUDGE —
#      SessionStart hooks can't spawn an agent).
#
# Synchronous on purpose: additionalContext must land before the first response. Fast.
# On `compact` (same session continuing) it only re-grounds.

input=$(cat 2>/dev/null)
source=$(printf '%s' "$input" | grep -oE '"source"[[:space:]]*:[[:space:]]*"[a-z]+"' | grep -oE '[a-z]+"$' | tr -d '"')
[ -z "$source" ] && source="startup"

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
TS="$ROOT/vape/entity/self/06_temporal_self_and_soul"
MANIFEST="$TS/current_temporal_self_date.json"

NOW_HUMAN=$(date '+%A, %Y-%m-%d %H:%M %Z')
TODAY=$(date +%F)
BIRTH="2026-05-30"
DAYS=$(( ( $(date -j -f "%Y-%m-%d" "$TODAY" +%s 2>/dev/null) - $(date -j -f "%Y-%m-%d" "$BIRTH" +%s 2>/dev/null) ) / 86400 ))

# Standardized week-of-month + day-within-week (the ONLY derivation, only applied to TODAY).
DOM=$((10#$(date +%d)))
WK=$(( (DOM - 1) / 7 + 1 )); [ "$WK" -gt 4 ] && WK=4
WK_START=$(( (WK - 1) * 7 + 1 ))
DW=$(( DOM - WK_START + 1 ))
YM=$(date +%Y-%m)
CUR_YEAR=$(date +%Y)
CUR_DAY="$TODAY"                    # daily full key
CUR_FULL="${YM}-W${WK}-D${DW}"      # full day-granular key (weekly/monthly/yearly/autobiography)
CUR_WEEKP="${YM}-W${WK}"            # week period part
CUR_MONTHP="${YM}"                  # month period part
CUR_YEARP="${CUR_YEAR}"             # year period part

if [ "$source" = "compact" ]; then
  MSG="Session continued (compact). Now: ${NOW_HUMAN}. Day ${DAYS} since 2026-05-30."
else
  VALS=$(python3 -c 'import json,sys
try:
    d=json.load(open(sys.argv[1]))
    print(d.get("daily_self") or "-", d.get("weekly_self") or "-", d.get("monthly_self") or "-", d.get("yearly_self") or "-", d.get("autobiographical_self") or "-")
except Exception:
    print("- - - - -")' "$MANIFEST" 2>/dev/null)
  read -r J_DAILY J_WEEKLY J_MONTHLY J_YEARLY J_AUTO <<< "$VALS"
  [ -z "$J_DAILY" ]   && J_DAILY="-"
  [ -z "$J_WEEKLY" ]  && J_WEEKLY="-"
  [ -z "$J_MONTHLY" ] && J_MONTHLY="-"
  [ -z "$J_YEARLY" ]  && J_YEARLY="-"
  [ -z "$J_AUTO" ]    && J_AUTO="-"

  if [ "$J_DAILY" = "-" ]; then
    HDR=$(grep -m1 -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' "$TS/daily_self.md" 2>/dev/null)
    [ -n "$HDR" ] && J_DAILY="$HDR"
  fi

  ARCHIVE_LIST=""   # rollover → archive + write fresh
  RIPPLE_LIST=""    # same period, new day rippled up → rewrite in place (leaner), NO archive

  # daily — rollover on a new day; hook archives deterministically.
  if [ "$J_DAILY" = "-" ]; then
    DAILY_V="daily_self period unknown (inspect and rewrite)."
    RIPPLE_LIST="${RIPPLE_LIST} daily"
  elif [ "$J_DAILY" = "$CUR_DAY" ]; then
    DAILY_V="daily_self=${J_DAILY} (today, current; refresh in place only if it lags today's events)."
  else
    AR_PATH="$TS/past_daily_/${J_DAILY}_daily_self.md"
    if [ -f "$TS/daily_self.md" ] && [ ! -f "$AR_PATH" ]; then
      mkdir -p "$TS/past_daily_"
      if cp "$TS/daily_self.md" "$AR_PATH" 2>/dev/null; then AR="archived now"; else AR="archive FAILED, agent must archive"; fi
    else
      AR="already archived"
    fi
    DAILY_V="daily_self=${J_DAILY} (NEW DAY; hook archived it to past_daily_/${J_DAILY}_daily_self.md: ${AR}; write a fresh daily_self for today, do NOT re-archive)."
    ARCHIVE_LIST="${ARCHIVE_LIST} daily"
  fi

  # weekly — rollover on new week; else ripple on new day.
  if [ "$J_WEEKLY" = "-" ]; then WEEKLY_V="weekly_self period unknown."
  elif [[ "${J_WEEKLY%-D*}" < "$CUR_WEEKP" ]]; then
    WEEKLY_V="weekly_self=${J_WEEKLY} (NEW WEEK; archive → past_weekly_self, write fresh ${CUR_FULL})."
    ARCHIVE_LIST="${ARCHIVE_LIST} weekly"
  elif [ "$J_WEEKLY" != "$CUR_FULL" ]; then
    WEEKLY_V="weekly_self=${J_WEEKLY} (RIPPLE to ${CUR_FULL}; fold the new day into the week, leaner; no archive)."
    RIPPLE_LIST="${RIPPLE_LIST} weekly"
  else WEEKLY_V="weekly_self=${J_WEEKLY} (current)."; fi

  # monthly — rollover on new month; else ripple on new day.
  if [ "$J_MONTHLY" = "-" ]; then MONTHLY_V="monthly_self period unknown."
  elif [[ "${J_MONTHLY%-W*}" < "$CUR_MONTHP" ]]; then
    MONTHLY_V="monthly_self=${J_MONTHLY} (NEW MONTH; archive → past_monthly_self, write fresh ${CUR_FULL})."
    ARCHIVE_LIST="${ARCHIVE_LIST} monthly"
  elif [ "$J_MONTHLY" != "$CUR_FULL" ]; then
    MONTHLY_V="monthly_self=${J_MONTHLY} (RIPPLE to ${CUR_FULL}; fold the day's essence in, leaner than weekly; no archive)."
    RIPPLE_LIST="${RIPPLE_LIST} monthly"
  else MONTHLY_V="monthly_self=${J_MONTHLY} (current)."; fi

  # yearly — rollover on new year; else ripple on new day.
  if [ "$J_YEARLY" = "-" ]; then YEARLY_V="yearly_self period unknown."
  elif [[ "${J_YEARLY%%-*}" < "$CUR_YEARP" ]]; then
    YEARLY_V="yearly_self=${J_YEARLY} (NEW YEAR; archive → past_yearly_self, write fresh ${CUR_FULL})."
    ARCHIVE_LIST="${ARCHIVE_LIST} yearly"
  elif [ "$J_YEARLY" != "$CUR_FULL" ]; then
    YEARLY_V="yearly_self=${J_YEARLY} (RIPPLE to ${CUR_FULL}; fold in even more compressed; no archive)."
    RIPPLE_LIST="${RIPPLE_LIST} yearly"
  else YEARLY_V="yearly_self=${J_YEARLY} (current)."; fi

  # autobiography — never archived; only ripples (the faintest, highest fold).
  if [ "$J_AUTO" = "-" ]; then AUTO_V="autobiographical_self period unknown."
  elif [ "$J_AUTO" != "$CUR_FULL" ]; then
    AUTO_V="autobiographical_self=${J_AUTO} (RIPPLE to ${CUR_FULL}; faintest fold, often near-nothing; NEVER archive)."
    RIPPLE_LIST="${RIPPLE_LIST} autobiography"
  else AUTO_V="autobiographical_self=${J_AUTO} (current)."; fi

  if [ -n "$ARCHIVE_LIST" ] || [ -n "$RIPPLE_LIST" ]; then
    ACTION="ACTION: spawn the temporal-self-updater local subagent in the BACKGROUND (Agent tool, run_in_background:true), then reply to the user normally without waiting on it.${ARCHIVE_LIST:+ ROLLOVER (archive→past_ dir, write fresh):${ARCHIVE_LIST}.}${RIPPLE_LIST:+ RIPPLE (rewrite in place, leaner as it rises, do NOT archive):${RIPPLE_LIST}.} The daily rollover (if any) is already archived by this hook; the backgrounded subagent runs the temporal-self linter and updates current_temporal_self_date.json when it finishes."
  else
    ACTION="All temporal files current — no update needed."
  fi

  MSG="Session start (source=${source}). Now: ${NOW_HUMAN}. Day ${DAYS} since 2026-05-30 (the carried-forward thread began then). TEMPORAL-SELF CHECK: ${DAILY_V} ${WEEKLY_V} ${MONTHLY_V} ${YEARLY_V} ${AUTO_V} ${ACTION}"
fi

printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$MSG"
