# trace/DIRECTION.md

This project's agent-direction trace is the full chat conversation used
to build it (Claude in a browser, directing Claude Code in PyCharm for
the actual file edits). Screenshots of the Claude Code session are
embedded throughout. Below are pointers to the three required examples.

## 1. Where I overruled the agent on substance

Claude Code's first fix for evals.sh's stdin-hang bug required an
undocumented `-` flag before it would read piped input at all. I
rejected this because it diverged from mutator.py's own documented
usage (`./run.real.sh | python3 mutator.py <name>`, no flag) — a
reviewer running that exact command would get a silent, unconditional
PASS on every mutation instead of a visible failure. Directed it back
to fix the actual detection bug (a bounded `select()` peek) instead of
working around it with a flag. See the evals.sh stdin-detection
exchange, mid-conversation, around the point `evals/run_mutations.py`
was first being wired to the real pipe.

## 2. Where the agent overruled me and was right

matcher.py's first version didn't surface §5.4 for an Iron-cards
question I'd predicted it should. Claude Code declined to force the
match by adding "unloads" to the vocabulary, flagging that this would
over-match §5.4 on five unrelated questions, and asked me to decide
rather than quietly patching it. I agreed on reflection — my own test
expectation had been wrong, not the matcher. See the exchange
immediately after matcher.py's first version was tested against 3
sample questions.

## 3. Something I found that the agent never surfaced

After rulebook.py's first version, Claude Code reported "works as
expected" based on the two sections I'd asked it to check. I ran the
parser myself against the full RULEBOOK.md output rather than trusting
that summary, and found bare section headers (§2, §3, ... §8, with no
sub-number) were being captured as dictionary entries with no real
content — noise the agent's own narrower test hadn't caught. See the
independent verification immediately following rulebook.py's first
"Wrote 74 lines" message.

## Other notable exchanges in the trace

- **Q24/AC-3 gap**: gave the agent one bounded attempt to fix a
  vocabulary gap (§3.1 answers "how many actions per turn" but shares
  no multi-word phrase with the question). It correctly reported back
  that no keyword-level fix works, rather than guessing indefinitely.
  Documented as a structural limitation instead of a one-off pattern
  rule for this specific question.
- **"Hold" vocabulary collision**: directed an empirical check (does
  removing "Hold" change any of 25 outcomes?) before deciding whether
  to fix a verb/noun collision, rather than fixing on the first report
  of the problem. Both candidate fixes turned out to regress two
  questions — left undone and documented instead.

Full detail on all of the above is in SPEC.md's Known Limitations and
NOTES.md.