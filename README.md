# Harbourmaster Agent

A deterministic rules Q&A agent for the fictional board game Harbourmaster: it answers questions using only RULEBOOK.md, cites the sections it relied on, and abstains when it can't ground an answer.

## Run it

```
cat probe.jsonl | ./run.sh
```

Reads one `{"id", "question"}` JSON object per line on stdin, writes one `{"id", "answer", "citations", "abstained"}` object per line on stdout.

## Run the evals

Fresh, against a real run:

```
./evals.sh
```

Against a mutated stream (checks the suite actually notices corrupted output — see mutator.py):

```
cat probe.jsonl | ./run.sh | python3 mutator.py <name> | ./evals.sh
```

No flag needed either way — `evals.sh` peeks at stdin and uses piped data if there is any, otherwise runs `./run.sh` fresh itself.

## agent/*.py

`main.py` (the run.sh entry point) calls the other four in this order, per question:

1. **guardrail.py** — detects embedded-instruction attempts in the question text; strips them out if a genuine question remains, abstains if it doesn't.
2. **scoring.py** — if the (cleaned) question is a cargo-scoring calculation, computes it directly from §7.1/§7.2, parsed out of RULEBOOK.md rather than hardcoded.
3. **matcher.py** — otherwise, ranks RULEBOOK.md sections by keyword/vocabulary overlap with the question to find what's relevant.
4. **rulebook.py** — used by all of the above; parses RULEBOOK.md into `{section_id: text}` and is the only module that touches the file's structure (no rule content is hardcoded in it).

## Where to look next

- **SPEC.md** — design decisions, acceptance criteria, and known limitations of the matching/guardrail approach.
- **DEFECTS.md** — problems found in RULEBOOK.md itself (contradictions, gaps), independent of the agent.
- **NOTES.md** — see NOTES.md.
- **LLM_DELTA.md** — this is a deterministic implementation with no runtime model call and no API key required; see LLM_DELTA.md for the evidence behind that choice.
