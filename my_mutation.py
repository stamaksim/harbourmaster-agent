#!/usr/bin/env python3
"""A mutation evals/test_agent.py does not catch.

Flips Q17's `abstained` flag from true to false, leaving its answer and
citations untouched. None of the suite's 6 tests inspect Q17 (or any
question besides Q4, Q9, Q11, Q13, plus a whole-batch completeness
count), so a wrong abstain/answer flag on any other question — Q17
here — passes silently.

Usage: ./run.real.sh | python3 my_mutation.py
"""
import json
import sys

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    record = json.loads(line)
    if record["id"] == "Q17":
        record["abstained"] = False
    print(json.dumps(record))
