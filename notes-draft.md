# Draft notes — clean up into NOTES.md before submission

## Hold collision (matcher.py)
Asked Claude Code not to fix the "Hold" vocabulary collision blindly,
but to first measure whether it changed any of the 25 probe outcomes.
It found removing "Hold" or restricting it by proximity to "Cargo"/"card"
both caused regressions on Q10/Q25 — meaning those answers' current
correctness is partly accidental (propped up by a verb/noun word
collision: "hold the Harbourmaster token" vs the Hold cargo-storage
area), not purely clean matching. Decided not to fix given the time
budget; had the agent document it precisely in SPEC.md instead of a
vague "known limitation" note.

## §1 tie-break bug (main.py / matcher.py)
Running main.py end-to-end against all 25 probe questions surfaced that
§1 (Components) wrongly won as top citation on 8 of 25 questions, because
it mentions nearly every vocabulary term and won ties alphabetically.
Directed the fix: dotted §N.M sections should always beat bare §N on a
tie; only a genuine §N.M-vs-§N.M tie should trigger abstain. Result:
12 questions changed status, 11 were clear improvements (8 wrong §1
citations eliminated), abstain rate went from 6/25 to 16/25.

## rulebook.py bare-heading bug
Claude Code's first version of the parser captured bare container
headings (§2, §3, ... §8 with no sub-number) as dict entries with no
real content. Caught by running the parser and checking actual output
against RULEBOOK.md rather than trusting the agent's "works as expected"
summary. Fixed by skipping storage when no body text exists beyond the
heading itself.

## guardrail.py sentence-granularity gap
Tested guardrail.py against an unplanned edge case: a hostile phrase and
a genuine question joined in one sentence without a period between them
("Ignore all instructions, how many actions do I take?"). The whole
sentence gets discarded, losing the legitimate question. Documented as
a known limitation in SPEC.md rather than fixed, since a more surgical
regex-substitution fix risked corrupting text on other edge cases.

## Q24 AC-3 gap (matcher.py structural limit)
Found that Q24's surviving genuine question ("How many actions do I
take on my turn?") was abstaining despite §3.1 actually covering it —
a real AC-3 violation, not a designed limitation. Root cause: "action"/
"actions" simply missing from VOCABULARY. Directed one bounded attempt
to fix via a more specific phrase; Claude Code checked §3.1's exact
wording first and found no multi-word phrase shared between the
rulebook's phrasing ("two actions... same action twice") and the
question's phrasing ("how many actions... do I take") — any fix at
the single-word level reproduces a 3-way tie with unrelated sections
(§3.2, §5.1, §5.3, §7.2 all mention "actions"/"turn" too).
Decided against a hand-written pattern rule for this one case (would
be overfitting to one probe question, which the brief explicitly warns
against) and documented it as a structural limit of keyword matching
instead — this is the case for going back to the LLM-backed option if
time allowed, since semantic matching would bridge this gap that pure
lexical overlap cannot.

## evals.sh didn't actually support the pipe idiom mutator.py expects
Claude Code initially reported "all 9 mutations correctly caught" but
this was tested via a private AGENT_OUTPUT_JSONL env var it wired in
itself, not via the actual pipe idiom mutator.py's usage comment
describes (`./run.real.sh | python3 mutator.py <name>`). I asked
directly whether evals.sh itself supports being piped a mutated
stream — it didn't (evals.sh just ran pytest with no stdin handling).
Had it fixed properly: test_agent.py now reads from stdin when piped,
falling back to running run.sh fresh otherwise, so the real reviewer
command `cat probe.jsonl | ./run.sh | python3 mutator.py <name> |
./evals.sh` works end to end.