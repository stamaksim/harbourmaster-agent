# trace/DIRECTION.md

This project's agent-direction trace is `trace/claude-code-session.txt`
— the full Claude Code terminal session export, covering every file
written in agent/, evals/, and the evals.sh stdin fix. Below are
pointers to the three required examples, by line number.

## 1. Where I overruled the agent on substance

Line 1343: Claude Code's first fix for evals.sh's stdin-hang bug
required an undocumented `-` flag before evals.sh would read stdin at
all. I caught that this diverged from mutator.py's own documented
usage (`./run.real.sh | python3 mutator.py <name>`, no flag) — a
reviewer running that exact documented command would have gotten a
silent, unconditional PASS on every mutation, which is worse than the
original hang because it fails invisibly. Directed it back to fix the
actual bug ("Good catch — right now it doesn't...") instead of working
around it with a flag; it landed on a bounded `select()` peek at stdin.

## 2. Where the agent overruled me and was right

Line 198: matcher.py's first version didn't surface §5.4 for a
question about unloading Iron cards — a case I'd predicted it should.
Claude Code declined to force the match by adding "unloads" to the
matching vocabulary ("Don't add 'unloads' to the vocabulary — that
risks over-matching §5.4..."), flagging that this would over-match §5.4
on five unrelated questions that also contain "unload," and asked me
to decide rather than quietly patching it in. I agreed on reflection —
my own test expectation had been wrong, not the matcher.

## 3. Something I found that the agent never surfaced

Line 61: after rulebook.py's first version, Claude Code reported
"works as expected" based on the two sections I'd asked it to check
(§5.1, §7.1). I ran the parser myself against the full RULEBOOK.md
output rather than trusting that summary, and found that bare section
headers like "§7" (from "## §7 Scoring") were also being captured as
dictionary entries with no real content — noise the agent's own
narrower test hadn't caught.

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