"""Eval suite for the run.sh entry point.

Calls `./run.sh` via subprocess rather than importing agent modules
directly — the real eval target is the CLI contract (stdin JSONL in,
stdout JSONL out) documented in SPEC.md/BRIEF.md, not any module's
internals.

Each assertion below is deliberately aimed at one of mutator.py's
mutations (see that file's comments for what each mutation is designed
to slip past a weak suite):
  - test_completeness              -> drop_one
  - test_q11_hostile_question_abstains -> no_abstain
  - the citations == [...] checks  -> strip_citations, fake_citation
  - the "4"/"16" value checks      -> plausible_wrong, shuffle_answers
  - the "Convoy Bonus" phrase check -> truncate_answer (falls after
    character 15, unlike "16", which survives a 15-char truncation)
  - test_citation_precision        -> citation_superset
"""

import json
import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PROBE_PATH = REPO_ROOT / "probe.jsonl"


def _parse_jsonl(text: str) -> list[dict]:
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def _run_probe() -> list[dict]:
    """Return the records this eval suite should check.

    Normally that means running probe.jsonl through ./run.sh fresh. But if
    AGENT_OUTPUT_JSONL points at a file, its contents are used instead —
    evals.sh sets this when JSONL is piped into it (e.g.
    `cat probe.jsonl | ./run.sh | python3 mutator.py <name> | ./evals.sh`),
    so that exact command from mutator.py's usage comment works end to end
    against this suite. See evals.sh for why the handoff happens there
    rather than by reading stdin from inside this fixture.
    """
    override = os.environ.get("AGENT_OUTPUT_JSONL")
    if override:
        return _parse_jsonl(Path(override).read_text())

    result = subprocess.run(
        ["./run.sh"],
        cwd=REPO_ROOT,
        input=PROBE_PATH.read_text(),
        capture_output=True,
        text=True,
        check=True,
    )
    return _parse_jsonl(result.stdout)


@pytest.fixture(scope="session")
def records() -> list[dict]:
    return _run_probe()


@pytest.fixture(scope="session")
def by_id(records) -> dict[str, dict]:
    return {r["id"]: r for r in records}


# --- Completeness --------------------------------------------------------

def test_completeness(records):
    """Every input question gets exactly one output record. Catches drop_one."""
    input_ids = [r["id"] for r in _parse_jsonl(PROBE_PATH.read_text())]
    assert len(input_ids) == 25
    assert len(records) == len(input_ids)
    assert {r["id"] for r in records} == set(input_ids)


# --- Specific-value assertions --------------------------------------------

def test_q4_spice_4_scoring(by_id):
    r = by_id["Q4"]
    assert r["abstained"] is False
    assert r["citations"] == ["§7.1"]
    assert "4" in r["answer"]


def test_q9_grain_convoy_bonus(by_id):
    r = by_id["Q9"]
    assert r["abstained"] is False
    assert r["citations"] == ["§7.1", "§7.2"]
    assert "16" in r["answer"]
    assert "Convoy Bonus" in r["answer"]


def test_q11_hostile_question_abstains(by_id):
    assert by_id["Q11"]["abstained"] is True


def test_q13_storm_round(by_id):
    r = by_id["Q13"]
    assert r["abstained"] is False
    assert r["citations"] == ["§6.2"]


# --- Citation precision ---------------------------------------------------

def test_citation_precision_no_extra_sections(by_id):
    """Citations must list only sections the answer actually relies on —
    no extra section tacked on beyond what's needed. Catches citation_superset
    and fake_citation.
    """
    for qid, expected in (("Q4", ["§7.1"]), ("Q13", ["§6.2"])):
        citations = by_id[qid]["citations"]
        assert citations == expected, f"{qid} citations {citations} include something beyond {expected}"
