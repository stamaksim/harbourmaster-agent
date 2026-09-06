# NOTES.md

## 1. What your agent got wrong, and how you caught it

Claude Code's first fix for a stdin-detection hang in evals.sh (an
isatty() check that hung when piped a mutated stream) required an
undocumented `-` flag before evals.sh would read stdin at all. I caught
that this diverged from mutator.py's own documented usage
(`./run.real.sh | python3 mutator.py <name>`, no flag): a reviewer
running that exact command would get a silent, unconditional PASS on
every mutation, since evals.sh would never look at the piped stream
without the flag. That's worse than the original hang, which was at
least visible. I sent it back to fix the actual bug instead of working
around it with a flag. It landed on a bounded `select()` peek at stdin,
which distinguishes a real pipe from an idle terminal in about two
seconds with no flag and no hang risk, verified against all three
required scenarios (no pipe, piped-unmutated, piped-mutated) with the
exact command mutator.py documents.

## 2. One thing you deliberately didn't do, and why

Q24's surviving genuine question ("how many actions do I take on my
turn?") is answerable from §3.1, but shares no multi-word phrase with
the rulebook's wording ("two actions... same action twice"), so
matcher.py's keyword approach can't ground it. I gave the agent one
bounded attempt at a vocabulary fix rather than unlimited tries; it
correctly reported back that no keyword-level fix could isolate §3.1
without re-tying it to unrelated sections (§3.2, §5.1, §5.3, §7.2 all
share the same generic words). I chose not to write a hand-written
pattern rule to force this one case to pass — that would be overfitting
to a single probe question rather than improving the general approach,
which the brief explicitly warns against. Documented as a structural
limit of keyword matching in SPEC.md instead, confirmed independently
in LLM_DELTA.md: a model reading the same two passages resolves it
immediately, which is the concrete case for a model-driven approach
over pure keyword overlap.

## 3. What you'd do with another day

Two matcher.py limitations share a root cause, confirmed by Probe B:
a broad, term-dense section (§1, Components) can outscore a genuinely
relevant §N.M section outright on raw shared-term count, not just tie
with it — this caused a real wrong citation on QB3, and Q10 wrongly
matched to §1 under one vocabulary configuration. A real fix would
discount broad summary sections or weight term specificity, rather than
the exact-tie-only tie-break I shipped. I'd also add "Lighthouse" and
related §9 terms to VOCABULARY now that the amendment is applied, fix
main.py's scoring-question detection to recognize QB4's phrasing
("worth 2, 4 and 5" rather than "values 1, 2, 3 and 5"), and wire
PROBE_B.jsonl into evals/test_agent.py so the suite isn't structurally
blind to any future regression on these ten questions — right now none
of the six tests would catch QB3, QB4, QB7, or QB8 getting worse.
Finally, I'd extend the citation model to allow synthesizing two
sections into one answer, since QB8 shows a case (Sail to/from the
Lighthouse) that genuinely needs both §4.3 and §9.2 together, which the
current single-best-section design can't represent.