#!/usr/bin/env python3
"""Run every mutator.py mutation through the real ./evals.sh pipe.

Captures one baseline `cat probe.jsonl | ./run.sh` run, then for each
mutation runs the exact reviewer-facing command end to end, matching
mutator.py's own documented usage with no extra flag:

    <baseline output> | python3 mutator.py <mutation> | ./evals.sh

evals.sh (not this script) is what makes that pipe work: it does a
short, bounded select() peek at stdin, and if a real pipe is feeding it,
captures that to a temp file and points evals/test_agent.py at it via
AGENT_OUTPUT_JSONL — pytest's own capturing would otherwise eat a
fixture's attempt to read stdin directly. See evals.sh's comment for why
that peek isn't just `[ ! -t 0 ]` or a required flag. The suite should fail on
every real mutation and pass only on "none" — that's the check that the
suite itself, not the harness, is doing the catching. Prints a
pass/fail matrix and exits non-zero if any mutation doesn't behave as
expected.
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

MUTATIONS = [
    "none",
    "no_abstain",
    "strip_citations",
    "shuffle_answers",
    "truncate_answer",
    "plausible_wrong",
    "citation_superset",
    "drop_one",
    "fake_citation",
]


def main() -> int:
    baseline = subprocess.run(
        ["./run.sh"],
        cwd=REPO_ROOT,
        input=(REPO_ROOT / "probe.jsonl").read_text(),
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    results = {}
    for mutation in MUTATIONS:
        proc = subprocess.run(
            ["sh", "-c", f"python3 mutator.py {mutation} | ./evals.sh"],
            cwd=REPO_ROOT,
            input=baseline,
            capture_output=True,
            text=True,
        )
        results[mutation] = "PASS" if proc.returncode == 0 else "FAIL"

    expected_pass = {"none"}
    width = max(len(m) for m in MUTATIONS)
    header = f"{'mutation':<{width}}  {'suite':<6}  {'expected':<8}  ok?"
    print(header)
    print("-" * len(header))

    all_ok = True
    for mutation in MUTATIONS:
        expected = "PASS" if mutation in expected_pass else "FAIL"
        ok = results[mutation] == expected
        all_ok = all_ok and ok
        print(f"{mutation:<{width}}  {results[mutation]:<6}  {expected:<8}  {'ok' if ok else 'WRONG'}")

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
