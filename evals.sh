#!/bin/sh
# Plain `./evals.sh` runs the suite fresh against a real ./run.sh call.
# Piping JSONL in — matching mutator.py's own documented usage exactly,
# with no extra flag —
#   cat probe.jsonl | ./run.sh | python3 mutator.py <name> | ./evals.sh
# points the suite at that (possibly mutated) stream instead.
#
# Detecting "is a pipe actually feeding this" can't use `[ ! -t 0 ]`
# (confirmed unsafe: a non-interactive shell with stdin merely inherited,
# not deliberately piped, is also non-tty and would hang forever on a
# blocking read with no writer and no EOF; separately, /dev/null is also
# non-tty but reads as instant EOF, silently no-op'ing the check on some
# CI boxes) or an unconditional blocking read (same hang risk). Instead,
# this does a short, bounded, non-destructive `select()` peek: a real
# pipe always produces data or closes quickly, since its upstream
# (run.sh / mutator.py) is a fast, finite process — so a couple of
# seconds is enough to tell "data is coming" from "nothing is
# connected," without an arbitrary flag and without risking a hang.
HAS_STDIN=$(python3 -c '
import select, sys
ready, _, _ = select.select([sys.stdin], [], [], 2)
print("yes" if ready else "no")
')

if [ "$HAS_STDIN" = "yes" ]; then
    TMPFILE=$(mktemp)
    cat > "$TMPFILE"
    # select() reports /dev/null-style stdin as "ready" too (EOF counts),
    # so only treat this as real piped data if something was actually read.
    if [ -s "$TMPFILE" ]; then
        export AGENT_OUTPUT_JSONL="$TMPFILE"
    fi
fi

uv run pytest evals/ -v
STATUS=$?

if [ -n "$TMPFILE" ]; then
    rm -f "$TMPFILE"
fi

exit $STATUS
