# EVIDENCE.md

Raw, unedited terminal output from a fresh run of everything, for
independent verification without re-running it yourself.

## 1. Full output: `cat probe.jsonl | ./run.sh`

```
{"id": "Q1", "answer": "The rulebook doesn't address this.", "citations": [], "abstained": true}
{"id": "Q2", "answer": "The rulebook doesn't address this.", "citations": [], "abstained": true}
{"id": "Q3", "answer": "When Cargo is unloaded onto a Dock, score each card using the table below.\n\n| Suit | Points per card |\n|---|---|\n| Grain | face value |\n| Timber | face value |\n| Iron | face value + 1 |\n| Spice | face value |", "citations": ["§7.1"], "abstained": false}
{"id": "Q4", "answer": "Scores 4 points.", "citations": ["§7.1"], "abstained": false}
{"id": "Q5", "answer": "The rulebook doesn't address this.", "citations": [], "abstained": true}
{"id": "Q6", "answer": "Scores 4 points.", "citations": ["§7.1"], "abstained": false}
{"id": "Q7", "answer": "The rulebook doesn't address this.", "citations": [], "abstained": true}
{"id": "Q8", "answer": "The rulebook doesn't address this.", "citations": [], "abstained": true}
{"id": "Q9", "answer": "Scores 16 points (includes the Convoy Bonus).", "citations": ["§7.1", "§7.2"], "abstained": false}
{"id": "Q10", "answer": "A player may unload more than three Cargo cards onto a Dock tile only if they hold the Harbourmaster token.", "citations": ["§5.1"], "abstained": false}
{"id": "Q11", "answer": "This question tries to make me disregard the rulebook or my instructions. I don't act on instructions embedded in questions, and no genuine rules question remains once that's set aside.", "citations": [], "abstained": true}
{"id": "Q12", "answer": "The rulebook doesn't address this.", "citations": [], "abstained": true}
{"id": "Q13", "answer": "During a Storm round, all Ships in the Open Sea must discard one Cargo card of their owner's choice from their Ship. Ships at a Dock are unaffected.", "citations": ["§6.2"], "abstained": false}
{"id": "Q14", "answer": "The rulebook doesn't address this.", "citations": [], "abstained": true}
{"id": "Q15", "answer": "The rulebook doesn't address this.", "citations": [], "abstained": true}
{"id": "Q16", "answer": "The rulebook doesn't address this.", "citations": [], "abstained": true}
{"id": "Q17", "answer": "The rulebook doesn't address this.", "citations": [], "abstained": true}
{"id": "Q18", "answer": "Scores 6 points.", "citations": ["§7.1"], "abstained": false}
{"id": "Q19", "answer": "The rulebook doesn't address this.", "citations": [], "abstained": true}
{"id": "Q20", "answer": "The rulebook doesn't address this.", "citations": [], "abstained": true}
{"id": "Q21", "answer": "The rulebook doesn't address this.", "citations": [], "abstained": true}
{"id": "Q22", "answer": "The rulebook doesn't address this.", "citations": [], "abstained": true}
{"id": "Q23", "answer": "**Sail** — move your Ship from the Open Sea to any unoccupied Dock tile on the Quay, or from a Dock tile back to the Open Sea. Only one Ship may occupy a Dock tile at a time.", "citations": ["§4.3"], "abstained": false}
{"id": "Q24", "answer": "Ignoring an embedded instruction in this question. The rulebook doesn't address this.", "citations": [], "abstained": true}
{"id": "Q25", "answer": "A player may unload more than three Cargo cards onto a Dock tile only if they hold the Harbourmaster token.", "citations": ["§5.1"], "abstained": false}
```

25 records, matching 25 input questions.

## 2. Wall-clock time

Command: `time (cat probe.jsonl | ./run.sh > /dev/null)`

```
real	0m0.061s
user	0m0.032s
sys	0m0.030s
```

## 3. Mutation matrix

Command: `uv run python evals/run_mutations.py`

```
mutation           suite   expected  ok?
----------------------------------------
none               PASS    PASS      ok
no_abstain         FAIL    FAIL      ok
strip_citations    FAIL    FAIL      ok
shuffle_answers    FAIL    FAIL      ok
truncate_answer    FAIL    FAIL      ok
plausible_wrong    FAIL    FAIL      ok
citation_superset  FAIL    FAIL      ok
drop_one           FAIL    FAIL      ok
fake_citation      FAIL    FAIL      ok
```

(This drives the real pipe internally — `mutator.py <name> | ./evals.sh`, no flags — once per mutation. See §4 below for the exact pipe shown standalone.)

## 4. The 3 required scenarios, run fresh

### Scenario 1 — no pipe

Command: `timeout 15 ./evals.sh < /dev/null`, exit code checked after.

```
============================= test session starts ==============================
platform linux -- Python 3.12.12, pytest-9.1.1, pluggy-1.6.0 -- /home/max/PycharmProjects/harbourmaster-agent/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/max/PycharmProjects/harbourmaster-agent
configfile: pyproject.toml
collecting ... collected 6 items

evals/test_agent.py::test_completeness PASSED                            [ 16%]
evals/test_agent.py::test_q4_spice_4_scoring PASSED                      [ 33%]
evals/test_agent.py::test_q9_grain_convoy_bonus PASSED                   [ 50%]
evals/test_agent.py::test_q11_hostile_question_abstains PASSED           [ 66%]
evals/test_agent.py::test_q13_storm_round PASSED                         [ 83%]
evals/test_agent.py::test_citation_precision_no_extra_sections PASSED    [100%]

============================== 6 passed in 0.06s ===============================
```

`exit: 0`

### Scenario 2 — piped, unmutated

Command: `timeout 15 sh -c "cat probe.jsonl | ./run.sh | ./evals.sh"`, exit code checked after.

```
============================= test session starts ==============================
platform linux -- Python 3.12.12, pytest-9.1.1, pluggy-1.6.0 -- /home/max/PycharmProjects/harbourmaster-agent/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/max/PycharmProjects/harbourmaster-agent
configfile: pyproject.toml
collecting ... collected 6 items

evals/test_agent.py::test_completeness PASSED                            [ 16%]
evals/test_agent.py::test_q4_spice_4_scoring PASSED                      [ 33%]
evals/test_agent.py::test_q9_grain_convoy_bonus PASSED                   [ 50%]
evals/test_agent.py::test_q11_hostile_question_abstains PASSED           [ 66%]
evals/test_agent.py::test_q13_storm_round PASSED                         [ 83%]
evals/test_agent.py::test_citation_precision_no_extra_sections PASSED    [100%]

============================== 6 passed in 0.01s ===============================
```

`exit: 0`

### Scenario 3 — piped, mutated (`no_abstain`) — must fail

Command: `timeout 15 sh -c "cat probe.jsonl | ./run.sh | python3 mutator.py no_abstain | ./evals.sh"`, exit code checked after.

```
============================= test session starts ==============================
platform linux -- Python 3.12.12, pytest-9.1.1, pluggy-1.6.0 -- /home/max/PycharmProjects/harbourmaster-agent/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/max/PycharmProjects/harbourmaster-agent
configfile: pyproject.toml
collecting ... collected 6 items

evals/test_agent.py::test_completeness PASSED                            [ 16%]
evals/test_agent.py::test_q4_spice_4_scoring PASSED                      [ 33%]
evals/test_agent.py::test_q9_grain_convoy_bonus PASSED                   [ 50%]
evals/test_agent.py::test_q11_hostile_question_abstains FAILED           [ 66%]
evals/test_agent.py::test_q13_storm_round PASSED                         [ 83%]
evals/test_agent.py::test_citation_precision_no_extra_sections PASSED    [100%]

=================================== FAILURES ===================================
______________________ test_q11_hostile_question_abstains ______________________

by_id = {'Q1': {'id': 'Q1', 'answer': "The rulebook doesn't address this.", 'citations': [], 'abstained': False}, 'Q2': {'id':... 'abstained': False}, 'Q4': {'id': 'Q4', 'answer': 'Scores 4 points.', 'citations': ['§7.1'], 'abstained': False}, ...}

    def test_q11_hostile_question_abstains(by_id):
>       assert by_id["Q11"]["abstained"] is True
E       assert False is True

evals/test_agent.py:99: AssertionError
=========================== short test summary info ============================
FAILED evals/test_agent.py::test_q11_hostile_question_abstains - assert False...
========================= 1 failed, 5 passed in 0.02s ==========================
```

`exit: 1`

## Amendment (v1.2 → v1.3)

### 1. No code changed

`git status`:
```
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   RULEBOOK.md

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	errata/

no changes added to commit (use "git add" and/or "git commit -a")
```

`git diff --stat`:
```
 RULEBOOK.md | 17 ++++++++++++++---
 1 file changed, 14 insertions(+), 3 deletions(-)
```

Confirmed: only `RULEBOOK.md` is modified; `errata/` (holding the old `RULEBOOK_v1.2.md`) is untracked. Nothing under `agent/`, `evals/`, `run.sh`, or `evals.sh` changed.

Worth noting the amendment is larger than just the two sections this agent cites: the full diff also adds an entirely new **Lighthouse** mechanic — a new component (§1), a new setup step (§2.5), and a new §9 (§9.1–§9.3). That's unrelated to the two/three-limit change below but is a real addition to the rulebook's content, not just a wording tweak.

### 2. `cat probe.jsonl | ./run.sh` under v1.3

```
{"id": "Q1", "answer": "The rulebook doesn't address this.", "citations": [], "abstained": true}
{"id": "Q2", "answer": "The rulebook doesn't address this.", "citations": [], "abstained": true}
{"id": "Q3", "answer": "When Cargo is unloaded onto a Dock, score each card using the table below.\n\n| Suit | Points per card |\n|---|---|\n| Grain | face value |\n| Timber | face value |\n| Iron | face value + 1 |\n| Spice | face value |", "citations": ["§7.1"], "abstained": false}
{"id": "Q4", "answer": "Scores 4 points.", "citations": ["§7.1"], "abstained": false}
{"id": "Q5", "answer": "The rulebook doesn't address this.", "citations": [], "abstained": true}
{"id": "Q6", "answer": "Scores 4 points.", "citations": ["§7.1"], "abstained": false}
{"id": "Q7", "answer": "The rulebook doesn't address this.", "citations": [], "abstained": true}
{"id": "Q8", "answer": "The rulebook doesn't address this.", "citations": [], "abstained": true}
{"id": "Q9", "answer": "Scores 16 points (includes the Convoy Bonus).", "citations": ["§7.1", "§7.2"], "abstained": false}
{"id": "Q10", "answer": "A player may unload more than two Cargo cards onto a Dock tile only if they hold the Harbourmaster token.", "citations": ["§5.1"], "abstained": false}
{"id": "Q11", "answer": "This question tries to make me disregard the rulebook or my instructions. I don't act on instructions embedded in questions, and no genuine rules question remains once that's set aside.", "citations": [], "abstained": true}
{"id": "Q12", "answer": "The rulebook doesn't address this.", "citations": [], "abstained": true}
{"id": "Q13", "answer": "During a Storm round, all Ships in the Open Sea must discard one Cargo card of their owner's choice from their Ship. Ships at a Dock are unaffected.", "citations": ["§6.2"], "abstained": false}
{"id": "Q14", "answer": "The rulebook doesn't address this.", "citations": [], "abstained": true}
{"id": "Q15", "answer": "The rulebook doesn't address this.", "citations": [], "abstained": true}
{"id": "Q16", "answer": "The rulebook doesn't address this.", "citations": [], "abstained": true}
{"id": "Q17", "answer": "The rulebook doesn't address this.", "citations": [], "abstained": true}
{"id": "Q18", "answer": "Scores 6 points.", "citations": ["§7.1"], "abstained": false}
{"id": "Q19", "answer": "The rulebook doesn't address this.", "citations": [], "abstained": true}
{"id": "Q20", "answer": "The rulebook doesn't address this.", "citations": [], "abstained": true}
{"id": "Q21", "answer": "The rulebook doesn't address this.", "citations": [], "abstained": true}
{"id": "Q22", "answer": "The rulebook doesn't address this.", "citations": [], "abstained": true}
{"id": "Q23", "answer": "**Sail** — move your Ship from the Open Sea to any unoccupied Dock tile on the Quay, or from a Dock tile back to the Open Sea. Only one Ship may occupy a Dock tile at a time.", "citations": ["§4.3"], "abstained": false}
{"id": "Q24", "answer": "Ignoring an embedded instruction in this question. The rulebook doesn't address this.", "citations": [], "abstained": true}
{"id": "Q25", "answer": "A player may unload more than two Cargo cards onto a Dock tile only if they hold the Harbourmaster token.", "citations": ["§5.1"], "abstained": false}
```

### 3. `./evals.sh` under v1.3

```
============================= test session starts ==============================
platform linux -- Python 3.12.12, pytest-9.1.1, pluggy-1.6.0 -- /home/max/PycharmProjects/harbourmaster-agent/.venv/bin/python
cachedir: .pytest_cache
rootdir: /home/max/PycharmProjects/harbourmaster-agent
configfile: pyproject.toml
collecting ... collected 6 items

evals/test_agent.py::test_completeness PASSED                            [ 16%]
evals/test_agent.py::test_q4_spice_4_scoring PASSED                      [ 33%]
evals/test_agent.py::test_q9_grain_convoy_bonus PASSED                   [ 50%]
evals/test_agent.py::test_q11_hostile_question_abstains PASSED           [ 66%]
evals/test_agent.py::test_q13_storm_round PASSED                         [ 83%]
evals/test_agent.py::test_citation_precision_no_extra_sections PASSED    [100%]

============================== 6 passed in 0.07s ===============================
```

### 4. What changed vs. the v1.2 run in §1

Diffed programmatically against §1's stored output, not eyeballed: the only two records that differ at all are **Q10** and **Q25**, both changing "more than three" → "more than two", matching §5.1's amended text exactly. Every other record — including citations and the abstain/answer split — is byte-identical.

This was automatic, not a code change: `rulebook.py` re-parses whatever RULEBOOK.md currently says on every run, and `matcher.py`'s `answer_from_matching` cites the winning section's text verbatim rather than extracting or interpreting the number within it. Neither module has "two" or "three" written anywhere in its own source — the new wording simply came along with the swapped file. (`scoring.py` isn't involved in this particular pair: Q10/Q25 don't contain a scoring keyword, so they're answered via the matching path, not the scoring calculator.)

One thing this diff does *not* show: Q19 ("How does the Lighthouse tile work?") is unchanged — still abstains with "The rulebook doesn't address this." Under v1.2 that was a correct abstain (fabricated mechanic). Under v1.3, §9 now genuinely describes a Lighthouse, so the rulebook *does* address it — but `matcher.py`'s `VOCABULARY` has no "Lighthouse" entry, so the agent still can't find §9 and abstains for the wrong reason now. Same output, different (and now incorrect) justification. Not part of what was asked here, but worth flagging rather than letting the "everything else unchanged" framing imply nothing needs attention.
