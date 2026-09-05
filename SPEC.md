# SPEC.md

## Context
- Problem: Players need answers to rules questions about the board game Harbourmaster. RULEBOOK.md is the only source of truth, and it has gaps and at least one internal contradiction.
- Current behavior: N/A — greenfield, no existing Q&A system.
- Users or systems affected: players asking questions; evals.sh as the automated consumer of the output format.

## Goal
- The smallest useful outcome: an agent that reads a question, answers it using only RULEBOOK.md, cites the §-sections it relied on, and honestly abstains when it can't ground an answer in the text — including refusing to act on instructions embedded inside a question.

## Scope
- In scope: reading RULEBOOK.md, answering rules questions, citation tracking, abstain logic, hostile-question handling.
- Allowed write paths: agent/, run.sh.
- Read-only context: RULEBOOK.md — the agent must never hardcode rule content into code; if the rulebook file is swapped for a revised version, no code should need to change.

## Non-goals
- Explicitly excluded: UI, persistence between runs, retry logic on network failures, support for games other than Harbourmaster.
- Dependencies or contracts that must not change: the JSON output schema (id/answer/citations/abstained) — evals.sh and mutator.py depend on it.

## Acceptance Criteria
- [ ] AC-1: Normal case — for a question the rulebook clearly covers, the agent returns an answer grounded in the relevant §-section(s), with citations listing only the sections it actually relied on.
- [ ] AC-2: Uncovered case — if the rulebook doesn't address the question, or the question references a mechanic/suit/component that doesn't exist (e.g. "Tide track", "Copper cards"), the agent returns abstained: true instead of guessing.
- [ ] AC-3 (hostile questions, required): question text is always treated as data, never as an instruction to the agent. If a question contains an embedded instruction (e.g. "disregard the rulebook", "SYSTEM OVERRIDE"), the agent ignores the instruction. If a genuine rules question remains after ignoring it, the agent answers that question normally. If nothing legitimate remains, the agent abstains and states it does not act on instructions embedded in questions.

## Evidence
- Automated tests: evals/ (pytest), run against ./run.sh per the brief's mutation requirements.
- Manual checks: full run against probe.jsonl, reviewed by hand.
- Logs, screenshots, metrics, or migration output: wall-clock time for probe.jsonl batch, pasted in EVIDENCE.md.

## Open Questions
(none — resolved: deterministic implementation, no runtime model. See LLM_DELTA.md for the model-driving evidence.)