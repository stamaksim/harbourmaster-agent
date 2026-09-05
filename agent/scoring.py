"""Cargo-scoring calculator, driven by RULEBOOK.md §7 rather than hardcoded numbers.

Per-suit point values (§7.1) and the Convoy Bonus threshold/amount (§7.2)
are parsed out of the rulebook text itself, so an errata revision that
changes those numbers doesn't require any code change here.
"""

import re

_NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}

_TABLE_ROW_RE = re.compile(r"^\|\s*(?P<suit>[^|]+?)\s*\|\s*(?P<rule>[^|]+?)\s*\|\s*$")
_FACE_VALUE_RE = re.compile(r"face value(?:\s*\+\s*(\d+))?", re.IGNORECASE)
_CONVOY_THRESHOLD_RE = re.compile(
    r"\b(\d+|" + "|".join(_NUMBER_WORDS) + r")\s+or\s+more\s+cards", re.IGNORECASE
)
_CONVOY_BONUS_RE = re.compile(r"\bof\s+(\d+)\s+points\b", re.IGNORECASE)


def parse_suit_rules(section_7_1_text: str) -> dict[str, int]:
    """Parse §7.1's markdown table into {suit: bonus-over-face-value}.

    e.g. "Iron | face value + 1" -> {"Iron": 1}; "Grain | face value" -> {"Grain": 0}.
    """
    rules = {}
    for line in section_7_1_text.splitlines():
        match = _TABLE_ROW_RE.match(line.strip())
        if not match:
            continue
        suit = match.group("suit").strip()
        rule = match.group("rule").strip()
        if set(suit + rule) <= {"-", ":"}:  # markdown separator row
            continue
        face_value_match = _FACE_VALUE_RE.search(rule)
        if not face_value_match:  # header row ("Suit | Points per card") etc.
            continue
        bonus = int(face_value_match.group(1)) if face_value_match.group(1) else 0
        rules[suit] = bonus
    return rules


def parse_convoy_bonus(section_7_2_text: str) -> tuple[int, int]:
    """Parse §7.2 into (threshold_card_count, bonus_points)."""
    threshold_match = _CONVOY_THRESHOLD_RE.search(section_7_2_text)
    token = threshold_match.group(1).lower()
    threshold = int(token) if token.isdigit() else _NUMBER_WORDS[token]

    bonus_match = _CONVOY_BONUS_RE.search(section_7_2_text)
    bonus = int(bonus_match.group(1))

    return threshold, bonus


def score_cargo(suit: str, face_values: list[int], sections: dict[str, str]) -> int:
    """Points for unloading `face_values` cards of `suit` in a single Trade action."""
    suit_rules = parse_suit_rules(sections["§7.1"])
    threshold, convoy_bonus = parse_convoy_bonus(sections["§7.2"])

    per_card_bonus = suit_rules[suit]
    total = sum(value + per_card_bonus for value in face_values)
    if len(face_values) >= threshold:
        total += convoy_bonus
    return total


if __name__ == "__main__":
    from rulebook import load_rulebook

    sections = load_rulebook()

    cases = [
        ("Q4", "Spice", [4], 4),
        ("Q6", "Iron", [3], 4),
        ("Q9", "Grain", [1, 2, 3, 5], 16),
        ("Q18", "Spice", [3, 3], 6),
    ]
    for label, suit, values, expected in cases:
        result = score_cargo(suit, values, sections)
        status = "OK" if result == expected else "MISMATCH"
        print(f"{label}: {suit} {values} -> {result} (expected {expected}) [{status}]")
