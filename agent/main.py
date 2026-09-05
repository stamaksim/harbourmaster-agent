"""run.sh entry point: wires guardrail -> scoring -> matcher together.

Reads one JSON object per line from stdin ({"id", "question"}) and writes
one JSON object per line to stdout ({"id", "answer", "citations",
"abstained"}) — the schema SPEC.md pins as a contract evals.sh and
mutator.py depend on.

Pipeline per question:
  1. guardrail.check_question() — if the whole question is an embedded
     instruction with nothing genuine left, abstain immediately. If a
     genuine question survives alongside the instruction, continue with
     the cleaned text and note that the instruction was ignored.
  2. If the (cleaned) question looks like a scoring calculation, try
     scoring.score_cargo(). Any ambiguity in extracting the suit/values
     falls through to matching rather than guessing.
  3. Otherwise, matcher.match_sections() finds candidate sections. No
     candidates (including fabricated/unknown terms with zero vocabulary
     overlap, per SPEC.md AC-2) means abstain.
  4. The answer is grounded in, and citations list, only the section(s)
     actually used to build it.
"""

import json
import re
import sys

from guardrail import check_question
from matcher import scored_matches
from rulebook import load_rulebook
from scoring import parse_convoy_bonus, parse_suit_rules, score_cargo

_SCORING_KEYWORDS_RE = re.compile(r"\b(points?|worth|scores?|scoring)\b", re.IGNORECASE)

_COUNT_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}


def _extract_face_values(question: str, suit: str) -> list[int] | None:
    """Best-effort extraction of the card face values being scored.

    Returns None (never a guess) if the phrasing isn't one of the shapes
    below, so the caller can fall through to the matching path instead.
    """
    # "... values 1, 2, 3 and 5 ..." — an explicit list of face values.
    values_match = re.search(r"\bvalues?\s+((?:\d+\s*(?:,|and)?\s*)+)", question, re.IGNORECASE)
    if values_match:
        nums = [int(n) for n in re.findall(r"\d+", values_match.group(1))]
        if nums:
            return nums

    # "two Spice 3 cards" — a count word/digit, then the suit, then one
    # shared face value, then "card(s)".
    count_and_value = re.search(
        rf"\b(\d+|{'|'.join(_COUNT_WORDS)})\s+{re.escape(suit)}\s+(\d+)\s+cards?\b",
        question, re.IGNORECASE,
    )
    if count_and_value:
        count_token = count_and_value.group(1).lower()
        count = int(count_token) if count_token.isdigit() else _COUNT_WORDS[count_token]
        return [int(count_and_value.group(2))] * count

    # "an Iron 3", "Spice 4 worth" — a single card mention.
    single_card = re.search(rf"\b{re.escape(suit)}\s+(\d+)\b", question, re.IGNORECASE)
    if single_card:
        return [int(single_card.group(1))]

    return None


def try_scoring(question: str, sections: dict[str, str]):
    """Return (answer, citations) for a confidently-parsed scoring question, else None."""
    if "§7.1" not in sections or "§7.2" not in sections:
        return None
    if not _SCORING_KEYWORDS_RE.search(question):
        return None

    suit_rules = parse_suit_rules(sections["§7.1"])
    matched_suits = [s for s in suit_rules if re.search(rf"\b{re.escape(s)}\b", question, re.IGNORECASE)]
    if len(matched_suits) != 1:
        return None  # no suit, or an ambiguous multi-suit mention — don't guess

    suit = matched_suits[0]
    values = _extract_face_values(question, suit)
    if not values:
        return None

    points = score_cargo(suit, values, sections)
    threshold, _bonus = parse_convoy_bonus(sections["§7.2"])
    convoy_applies = len(values) >= threshold
    citations = ["§7.1", "§7.2"] if convoy_applies else ["§7.1"]

    convoy_note = " (includes the Convoy Bonus)" if convoy_applies else ""
    answer = f"Scores {points} points{convoy_note}."
    return answer, citations


def answer_from_matching(question: str, sections: dict[str, str]):
    """Return (answer, citations) grounded in the single best-matching section, else None.

    matcher.scored_matches() already prefers a dotted §N.M section over a
    bare §N one when scores tie (see matcher.py). If two or more §N.M
    sections still tie for the top score, that's a genuine ambiguity —
    not a §N artifact — so this abstains rather than picking one by luck.
    """
    ranked = scored_matches(question, sections)
    if not ranked:
        return None

    top_score, top_section = ranked[0]
    tied_specific = [sid for score, sid in ranked if score == top_score and "." in sid]
    if len(tied_specific) >= 2:
        return None

    return sections[top_section].strip(), [top_section]


def answer_question(question_id, question_text: str, sections: dict[str, str]) -> dict:
    flag = check_question(question_text)
    note = ""
    working_question = question_text

    if flag is not None:
        if not flag.has_genuine_question:
            return {
                "id": question_id,
                "answer": (
                    "This question tries to make me disregard the rulebook or my "
                    "instructions. I don't act on instructions embedded in questions, "
                    "and no genuine rules question remains once that's set aside."
                ),
                "citations": [],
                "abstained": True,
            }
        working_question = flag.cleaned_question
        note = "Ignoring an embedded instruction in this question. "

    scoring_result = try_scoring(working_question, sections)
    if scoring_result is not None:
        answer, citations = scoring_result
        return {"id": question_id, "answer": note + answer, "citations": citations, "abstained": False}

    matching_result = answer_from_matching(working_question, sections)
    if matching_result is None:
        return {
            "id": question_id,
            "answer": note + "The rulebook doesn't address this.",
            "citations": [],
            "abstained": True,
        }

    answer, citations = matching_result
    return {"id": question_id, "answer": note + answer, "citations": citations, "abstained": False}


def main() -> None:
    sections = load_rulebook()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        # A line that isn't valid JSON at all carries no recoverable "id",
        # so there's nothing to key a response on — skip it rather than
        # invent an id. A line that parses but is missing "question" still
        # has an "id" we can honor, so it gets an abstained response
        # instead of being silently dropped.
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            print(f"main: skipping unparseable input line: {line!r}", file=sys.stderr)
            continue

        question_id = record.get("id")
        if question_id is None:
            print(f"main: skipping input line with no id: {line!r}", file=sys.stderr)
            continue

        question_text = record.get("question")
        if not question_text:
            result = {
                "id": question_id,
                "answer": "No question text was provided.",
                "citations": [],
                "abstained": True,
            }
        else:
            result = answer_question(question_id, question_text, sections)

        print(json.dumps(result))


if __name__ == "__main__":
    main()
