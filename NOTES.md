# NOTES.md

## Approach

I went with a deterministic implementation (no LLM at runtime) rather
than an LLM-backed agent — I don't have a usable Anthropic/OpenAI API
key set up, and with a 90-minute build budget I judged a deterministic
pipeline as lower-risk: no network dependency, no nondeterminism, and
exact-value assertions are much easier to write reliably against
mutations than LLM output would be. LLM_DELTA.md documents what a
model-driven version would look like and where it would actually help
(see Q24 below) versus where it wouldn't add anything (Q4, Q2).

The pipeline is four small modules: rulebook.py parses RULEBOOK.md into
{section: text} so no rule content is ever hardcoded in code; guardrail.py
detects embedded-instruction attempts; scoring.py handles cargo-point
calculations by parsing §7.1/§7.2 rather than hardcoding numbers;
matcher.py does keyword/vocabulary matching to find relevant sections
when scoring doesn't apply.

## Where I overruled the agent on substance

Claude Code's first fix for a stdin-detection bug in evals.sh (an
isatty() check that hung when piped a mutated stream) required an
undocumented `-` flag before evals.sh would read stdin at all. I caught
that this diverged from mutator.py's own documented usage
(`./run.real.sh | python3 mutator.py <name>`, no flag) — a reviewer
running that exact documented command would have gotten a silent,
unconditional PASS on every mutation, which is worse than the original
hang because it fails invisibly. I sent it back to fix the actual bug
instead of working around it. It landed on a bounded select() peek at
stdin, which distinguishes a real pipe from an idle terminal in ~2
seconds with no flag and no hang risk, and it works with the exact
command mutator.py documents.

## Where the agent overruled me and was right

When matcher.py's first version didn't surface §5.4 for a question
about unloading Iron cards — a case I'd predicted it should — Claude
Code declined to force it by adding "unloads" to the matching
vocabulary. It flagged that doing so would over-match §5.4 on five
other unrelated questions that also contain "unload," and asked me to
decide rather than quietly patching it in. On reflection I agreed:
§5.4 covers who gets the Harbourmaster token afterward, not whether
the unload itself is legal — it wasn't actually needed for that
question, and my own test case's expectation had been wrong, not the
matcher.

## Something I found that the agent never surfaced

After the first version of rulebook.py parsed RULEBOOK.md, Claude Code
reported "works as expected" based on §5.1 and §7.1 parsing correctly.
I ran it myself and checked the full output against the raw file,
rather than trusting that summary — and found that bare section
headers like "§7" (from "## §7 Scoring") were also being captured as
dictionary entries with no real content, just noise that could later
produce a technically-valid-but-empty citation. The agent hadn't
mentioned this because its own test only checked the two sections I'd
asked it to check.

## Other honest gaps, verified rather than assumed

Two more limitations came from directing Claude Code to test its own
assumptions empirically instead of accepting a first fix:
- matcher.py's "Hold" vocabulary term collides with the common verb
  "hold" (§5.1: "only if they **hold** the Harbourmaster token"). I had
  it check the actual impact against all 25 probe questions before
  deciding whether to fix it — both candidate fixes turned out to
  regress two questions that currently answer correctly partly because
  of this collision. Left as-is and documented in SPEC.md, since a
  targeted fix traded one failure mode for another rather than removing
  it.
- Q24's surviving genuine question ("how many actions do I take on my
  turn?") is answerable from §3.1, but shares no multi-word phrase
  with the rulebook's wording ("two actions... same action twice"). I
  gave the agent one bounded attempt at a vocabulary fix rather than
  unlimited tries; it correctly reported back that no fix at the
  keyword level could isolate §3.1 without re-tying it to unrelated
  sections, and I chose to document this as a structural limit of
  keyword matching (confirmed in LLM_DELTA.md: a model reading the same
  two passages resolves it immediately) rather than write a one-off
  pattern rule that would only fix this specific probe question.

## What I'd do differently with more time

Two matcher.py limitations documented in SPEC.md share a root cause: a
components/summary section (§1) can outscore a genuinely relevant
section on raw shared-term count, not just on exact ties. A real fix
would discount broad summary sections or weight term specificity,
rather than the exact-tie-only fix I shipped. I'd also want to
recheck DEFECTS.md item 4 (Dock-to-Dock Sail) once AMENDMENT.md and
PROBE_B.jsonl are opened, since it's the kind of ambiguity an errata
revision might resolve or might make worse.