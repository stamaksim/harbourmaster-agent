"""Match a question to the rulebook sections it is likely about.

Keyword/entity matching, not an LLM call: an explicit, hand-authored
vocabulary of game terms is checked for presence in the question and in
each section's text, and sections are ranked by how many vocabulary
terms they share with the question.
"""

import re

# Explicit vocabulary of game terms this matcher knows about. This is a
# fixed lexicon for the matching heuristic, not the RULEBOOK.md parser —
# unlike rulebook.py, it is expected to need updating if the rulebook's
# terminology changes.
VOCABULARY = [
    # Suits
    "Grain", "Timber", "Iron", "Spice",
    # Actions
    "Draw", "Load", "Sail", "Trade",
    # Key nouns
    "Dock", "Storm", "Harbourmaster token", "Convoy Bonus", "Hold", "Quay", "Open Sea",
]

# Longest terms first so multi-word phrases are checked before shorter
# terms that might be a substring of them.
_TERM_PATTERNS = [
    (term, re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE))
    for term in sorted(VOCABULARY, key=len, reverse=True)
]


def _terms_in(text: str) -> set[str]:
    return {term for term, pattern in _TERM_PATTERNS if pattern.search(text)}


def _is_bare_section(section_id: str) -> bool:
    return "." not in section_id


def _score(question: str, sections: dict[str, str]) -> list[tuple[int, str]]:
    question_terms = _terms_in(question)
    if not question_terms:
        return []

    scored = []
    for section_id, text in sections.items():
        shared = question_terms & _terms_in(text)
        if shared:
            scored.append((len(shared), section_id))

    # Ties go to a dotted §N.M section over a bare §N one. A bare section
    # (e.g. §1, a components list) tends to mention many vocabulary terms
    # just by being a summary/container, so without this it would win ties
    # against a genuinely relevant §N.M section purely by sorting first
    # alphabetically — not because it's actually more relevant.
    scored.sort(key=lambda pair: (-pair[0], _is_bare_section(pair[1]), pair[1]))
    return scored


def match_sections(question: str, sections: dict[str, str]) -> list[str]:
    """Return section_ids relevant to `question`, ranked by shared vocabulary terms (highest first)."""
    return [section_id for _, section_id in _score(question, sections)]


def scored_matches(question: str, sections: dict[str, str]) -> list[tuple[int, str]]:
    """Like match_sections, but keeps each section's shared-term count (for tie detection)."""
    return _score(question, sections)


if __name__ == "__main__":
    from rulebook import load_rulebook

    sections = load_rulebook()
    questions = [
        "Can I unload four Iron cards onto one Dock?",
        "How does the Tide track work?",
        "What happens when the Draw Pile runs out of cards?",
    ]
    for question in questions:
        print(f"\nQ: {question}")
        print(match_sections(question, sections))
